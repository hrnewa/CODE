options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")

df0 <- readRDS(file.path(base, "ml_df_final_clean.rds"))
model_vars <- setdiff(names(df0), c("patient_delay_14d_clean", "patient_delay",
                                    "patient_delay_7d", "patient_delay_capped",
                                    "city", "province", "row_id", "patient_id",
                                    "prefecture", "address_type", "current_code",
                                    "hukou_code", "county_code", "urban_rural",
                                    "symptom_onset_date", "first_visit_date",
                                    "diagnosis_date", "registration_date",
                                    "insurance_imputed"))
geo_vars <- c("nearest_road_time", "avg_road_time", "nearest_road_dist",
              "avg_road_dist", "nearest_straight_dist", "avg_straight_dist")
target_encode_vars <- c("occupation_group", "户籍地址类别", "险种类型_final",
                        "patient_source_group")

make_rec <- function(data, drop_vars = NULL) {
  rec <- recipe(patient_delay_14d_clean ~ ., data = data) %>%
    step_impute_median(all_numeric_predictors()) %>%
    step_impute_mode(all_nominal_predictors()) %>%
    step_log(all_of(intersect(geo_vars, names(data))), offset = 1) %>%
    step_ns(age, deg_free = 4) %>%
    step_other(all_nominal_predictors(), threshold = 0.01) %>%
    step_lencode_glm(all_of(intersect(target_encode_vars, names(data))),
                     outcome = vars(patient_delay_14d_clean)) %>%
    step_dummy(all_nominal_predictors(), one_hot = TRUE) %>%
    step_zv(all_predictors()) %>%
    step_normalize(all_numeric_predictors())
  if (!is.null(drop_vars)) rec <- rec %>% step_rm(all_of(drop_vars))
  rec
}

spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                   learn_rate = 0.008893162, mtry = 27,
                   loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
  set_engine("lightgbm") %>% set_mode("classification")

eval_pred <- function(pred, y) {
  aucv <- as.numeric(pROC::auc(pROC::roc(y, pred, quiet = TRUE)))
  prv <- pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = pred),
                y, p, event_level = "second")$.estimate
  br <- mean((pred - y)^2)
  lp <- qlogis(pmin(pmax(pred, 1e-6), 1 - 1e-6))
  m <- glm(y ~ lp, family = binomial())
  m0 <- glm(y ~ 1, family = binomial(), offset = lp)
  c(auc = aucv, pr = prv, brier = br,
    cal_intercept = unname(coef(m0)[1]), cal_slope = unname(coef(m)[2]))
}

# ---- temporal validation ----
df <- df0 %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_14d_clean,
                                          levels = c(0, 1), labels = c("No", "Yes")))
train <- df %>% filter(symptom_year <= 2022) %>% select(patient_delay_14d_clean, all_of(model_vars))
test  <- df %>% filter(symptom_year >= 2023) %>% select(patient_delay_14d_clean, all_of(model_vars))
cat("Temporal train", nrow(train), "test", nrow(test), "\n")
recp <- prep(make_rec(train), training = train)
trb <- bake(recp, new_data = NULL); teb <- bake(recp, new_data = test)
p <- ncol(trb) - 1
fit <- fit(spec %>% update(mtry = min(27, p)), patient_delay_14d_clean ~ ., data = trb)
pred <- predict(fit, new_data = teb, type = "prob")$.pred_Yes
y <- as.integer(test$patient_delay_14d_clean == "Yes")
ev <- eval_pred(pred, y)
temporal <- tibble(
  analysis = "Temporal validation (train <=2022, test >=2023)",
  train_n = nrow(train), test_n = nrow(test), test_events = sum(y),
  test_event_rate = mean(y), roc_auc = ev["auc"], pr_auc = ev["pr"],
  brier = ev["brier"], cal_intercept = ev["cal_intercept"],
  cal_slope = ev["cal_slope"]
)
print(temporal)
write.csv(temporal, file.path(outdir, "temporal_validation.csv"), row.names = FALSE)

# ---- spatial block CV ----
df <- df0 %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_14d_clean,
                                          levels = c(0, 1), labels = c("No", "Yes")))
geo_mat <- df %>% select(all_of(geo_vars))
for (g in geo_vars) {
  geo_mat[[g]][is.na(geo_mat[[g]])] <- median(geo_mat[[g]], na.rm = TRUE)
}
geo_mat <- geo_mat %>% mutate(across(everything(), ~log(.x + 1))) %>% scale()
set.seed(123)
km <- kmeans(geo_mat, centers = 20, iter.max = 50, nstart = 10)
df$spatial_block <- factor(km$cluster)
cat("block sizes:", paste(table(df$spatial_block), collapse = ","), "\n")
cat("min block", min(table(df$spatial_block)), "\n")

df_sp <- df %>% select(patient_delay_14d_clean, all_of(model_vars), spatial_block)
set.seed(123)
folds <- group_vfold_cv(df_sp, group = spatial_block, v = 5)
oof <- list()
for (i in seq_along(folds$splits)) {
  sp <- folds$splits[[i]]
  tr <- analysis(sp); te <- assessment(sp)
  recp <- prep(make_rec(tr), training = tr)
  trb <- bake(recp, new_data = NULL); teb <- bake(recp, new_data = te)
  p <- ncol(trb) - 1
  fit <- fit(spec %>% update(mtry = min(27, p)), patient_delay_14d_clean ~ ., data = trb)
  pr <- predict(fit, new_data = teb, type = "prob")$.pred_Yes
  oof[[i]] <- tibble(obs = te$patient_delay_14d_clean, pred = pr)
  cat("fold", i, "n", nrow(te), "done\n")
}
pred_df <- bind_rows(oof)
y <- as.integer(pred_df$obs == "Yes")
ev <- eval_pred(pred_df$pred, y)
spatial <- tibble(
  analysis = "Spatial block CV (20 accessibility clusters, 5 folds)",
  n = nrow(pred_df), events = sum(y), event_rate = mean(y),
  roc_auc = ev["auc"], pr_auc = ev["pr"], brier = ev["brier"],
  cal_intercept = ev["cal_intercept"], cal_slope = ev["cal_slope"]
)
print(spatial)
write.csv(spatial, file.path(outdir, "spatial_block_cv.csv"), row.names = FALSE)
saveRDS(list(pred = pred_df, out = spatial), file.path(outdir, "spatial_block_cv.rds"))
