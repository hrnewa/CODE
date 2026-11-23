options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels)
  library(tidyverse)
  library(bonsai)
  library(lightgbm)
  library(xgboost)
  library(ranger)
  library(glmnet)
  library(embed)
  library(pROC)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

df <- readRDS(file.path(base, "ml_df_final_clean.rds")) %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_14d_clean,
                                          levels = c(0, 1), labels = c("No", "Yes")))

model_vars <- setdiff(names(df), c("patient_delay_14d_clean", "patient_delay", "patient_delay_7d", "patient_delay_capped", "city", "province", "row_id", "patient_id", "prefecture", "address_type", "current_code", "hukou_code", "county_code", "urban_rural", "symptom_onset_date", "first_visit_date", "diagnosis_date", "registration_date", "insurance_imputed"))
geo_vars <- c("nearest_road_time", "avg_road_time", "nearest_road_dist",
              "avg_road_dist", "nearest_straight_dist", "avg_straight_dist")
target_encode_vars <- c("occupation_group", "户籍地址类别", "险种类型_final",
                        "patient_source_group")

set.seed(123)
split <- initial_split(df, prop = 0.7, strata = patient_delay_14d_clean)
train <- training(split)
test  <- testing(split)
cat("train:", nrow(train), " test:", nrow(test), "\n")
cat("test events:", sum(test$patient_delay_14d_clean == "Yes"), "\n")

rec <- recipe(patient_delay_14d_clean ~ ., data = train %>% select(patient_delay_14d_clean, all_of(model_vars))) %>%
  step_impute_median(all_numeric_predictors()) %>%
  step_impute_mode(all_nominal_predictors()) %>%
  step_log(all_of(geo_vars), offset = 1) %>%
  step_ns(age, deg_free = 4) %>%
  step_other(all_nominal_predictors(), threshold = 0.01) %>%
  step_lencode_glm(all_of(target_encode_vars),
                   outcome = vars(patient_delay_14d_clean)) %>%
  step_dummy(all_nominal_predictors(), one_hot = TRUE) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())

recp <- prep(rec, training = train %>% select(patient_delay_14d_clean, all_of(model_vars)))
train_b <- bake(recp, new_data = NULL)
test_b  <- bake(recp, new_data = test %>% select(patient_delay_14d_clean, all_of(model_vars)))
cat("baked train:", dim(train_b), " test:", dim(test_b), "\n")

p <- ncol(train_b) - 1

specs <- list(
  LightGBM = boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                        learn_rate = 0.008893162, mtry = min(27, p),
                        loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
    set_engine("lightgbm") %>% set_mode("classification"),
  XGBoost = boost_tree(trees = 1387, tree_depth = 6, min_n = 8,
                       learn_rate = 0.0085463591014363, mtry = min(27, p),
                       loss_reduction = 0.00472028160057033,
                       sample_size = 0.975519861528464) %>%
    set_engine("xgboost", eval_metric = "auc") %>% set_mode("classification"),
  `Random forest` = rand_forest(trees = 1000, min_n = 96, mtry = min(27, p)) %>%
    set_engine("ranger", importance = "permutation") %>% set_mode("classification"),
  `Elastic net` = logistic_reg(penalty = 1e-5, mixture = 0.2) %>%
    set_engine("glmnet") %>% set_mode("classification")
)

fit_one <- function(spec, label) {
  cat("Fitting", label, "...\n")
  fit(spec, patient_delay_14d_clean ~ ., data = train_b)
}

fits <- imap(specs, fit_one)
saveRDS(fits, file.path(outdir, "clean_models.rds"))

pred_list <- imap(fits, function(fit, label) {
  list(label = label,
       test = predict(fit, new_data = test_b, type = "prob")$.pred_Yes,
       train = predict(fit, new_data = train_b, type = "prob")$.pred_Yes)
})

pred_wide <- tibble(row = seq_len(nrow(test_b))) %>%
  bind_cols(as_tibble(setNames(lapply(pred_list, `[[`, "test"), names(pred_list))))

y_test <- as.integer(test$patient_delay_14d_clean == "Yes")
y_train <- as.integer(train$patient_delay_14d_clean == "Yes")

auc_fun <- function(y, p) as.numeric(pROC::auc(pROC::roc(y, p, quiet = TRUE)))
pr_fun <- function(y, p) {
  d <- tibble(y = factor(y, levels = c(0, 1)), p = p)
  pr_auc(d, y, p, event_level = "second")$.estimate
}
brier_fun <- function(y, p) mean((p - y)^2)
cal_fun <- function(y, p) {
  lp <- qlogis(pmin(pmax(p, 1e-6), 1 - 1e-6))
  m <- glm(y ~ lp, family = binomial())
  m0 <- glm(y ~ 1, family = binomial(), offset = lp)
  c(intercept = unname(coef(m0)[1]), slope = unname(coef(m)[2]))
}
threshold_fun <- function(y, p) {
  r <- pROC::roc(y, p, quiet = TRUE)
  as.numeric(pROC::coords(r, "best", ret = "threshold",
                          best.method = "youden")$threshold[1])
}

metric_one <- function(label, plist) {
  thr <- threshold_fun(y_train, plist$train)
  cls <- ifelse(plist$test >= thr, "Yes", "No")
  tp <- sum(cls == "Yes" & y_test == 1)
  fp <- sum(cls == "Yes" & y_test == 0)
  tn <- sum(cls == "No" & y_test == 0)
  fn <- sum(cls == "No" & y_test == 1)
  cal <- cal_fun(y_test, plist$test)
  tibble(
    model = label,
    threshold = thr,
    roc_auc = auc_fun(y_test, plist$test),
    pr_auc = pr_fun(y_test, plist$test),
    brier = brier_fun(y_test, plist$test),
    accuracy = (tp + tn) / length(y_test),
    sensitivity = tp / (tp + fn),
    specificity = tn / (tn + fp),
    ppv = tp / (tp + fp),
    npv = tn / (tn + fn),
    cal_intercept = cal[1],
    cal_slope = cal[2]
  )
}

metrics <- map2(names(pred_list), pred_list, metric_one)
metrics_tbl <- bind_rows(metrics)
print(metrics_tbl)
write.csv(metrics_tbl, file.path(outdir, "model_metrics.csv"), row.names = FALSE)

pred_out <- test %>%
  select(patient_delay_14d_clean, age, gender_clean, city, province,
         prefecture, county_code, urban_rural) %>%
  bind_cols(pred_wide %>% select(-row))
write.csv(pred_out, file.path(outdir, "test_predictions.csv"), row.names = FALSE)

# bootstrap CIs for LGB and difference vs XGB
set.seed(42)
B <- 1000
n <- length(y_test)
boot <- matrix(NA_real_, nrow = B, ncol = 10)
colnames(boot) <- c("lgb_auc", "lgb_pr", "lgb_brier", "xgb_auc", "xgb_pr",
                    "xgb_brier", "d_auc", "d_pr", "d_brier", "lgb_acc")
pl <- pred_wide$LightGBM
px <- pred_wide$XGBoost
thr_l <- metrics_tbl$threshold[metrics_tbl$model == "LightGBM"]
for (b in seq_len(B)) {
  idx <- sample.int(n, n, replace = TRUE)
  yb <- y_test[idx]; plb <- pl[idx]; pxb <- px[idx]
  boot[b, "lgb_auc"] <- auc_fun(yb, plb)
  boot[b, "lgb_pr"] <- pr_fun(yb, plb)
  boot[b, "lgb_brier"] <- brier_fun(yb, plb)
  boot[b, "xgb_auc"] <- auc_fun(yb, pxb)
  boot[b, "xgb_pr"] <- pr_fun(yb, pxb)
  boot[b, "xgb_brier"] <- brier_fun(yb, pxb)
  boot[b, "d_auc"] <- boot[b, "lgb_auc"] - boot[b, "xgb_auc"]
  boot[b, "d_pr"] <- boot[b, "lgb_pr"] - boot[b, "xgb_pr"]
  boot[b, "d_brier"] <- boot[b, "lgb_brier"] - boot[b, "xgb_brier"]
  boot[b, "lgb_acc"] <- mean(ifelse(plb >= thr_l, 1, 0) == yb)
}
ci <- function(x) quantile(x, c(0.025, 0.975), na.rm = TRUE)
boot_tbl <- tibble(
  metric = colnames(boot),
  estimate = c(auc_fun(y_test, pl), pr_fun(y_test, pl), brier_fun(y_test, pl),
               auc_fun(y_test, px), pr_fun(y_test, px), brier_fun(y_test, px),
               auc_fun(y_test, pl) - auc_fun(y_test, px),
               pr_fun(y_test, pl) - pr_fun(y_test, px),
               brier_fun(y_test, pl) - brier_fun(y_test, px),
               mean(ifelse(pl >= thr_l, 1, 0) == y_test)),
  ci_low = apply(boot, 2, ci)[1, ],
  ci_high = apply(boot, 2, ci)[2, ]
)
roc_l <- pROC::roc(y_test, pl, quiet = TRUE)
roc_x <- pROC::roc(y_test, px, quiet = TRUE)
dl <- pROC::roc.test(roc_l, roc_x, method = "delong")
cat("\nDeLong LGB vs XGB p =", dl$p.value, "\n")
boot_tbl$p_value <- NA_real_
boot_tbl$p_value[boot_tbl$metric == "d_auc"] <- dl$p.value
print(boot_tbl)
write.csv(boot_tbl, file.path(outdir, "bootstrap_metrics.csv"), row.names = FALSE)

saveRDS(list(split = split, recipe = recp, fits = fits, metrics = metrics_tbl,
             pred = pred_out, boot = boot_tbl),
        file.path(outdir, "clean_model_results.rds"))
cat("Saved to", outdir, "\n")
