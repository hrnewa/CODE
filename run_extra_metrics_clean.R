options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC); library(broom)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
res <- readRDS(file.path(outdir, "clean_model_results.rds"))
df <- readRDS(file.path(base, "ml_df_final_clean.rds")) %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_14d_clean,
                                          levels = c(0, 1), labels = c("No", "Yes")))
model_vars <- setdiff(names(df), c("patient_delay_14d_clean", "patient_delay",
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

set.seed(123)
split <- initial_split(df, prop = 0.7, strata = patient_delay_14d_clean)
train <- training(split); test <- testing(split)

make_rec <- function(data) {
  recipe(patient_delay_14d_clean ~ ., data = data) %>%
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
}

spec_lgb <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                       learn_rate = 0.008893162, mtry = 27,
                       loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
  set_engine("lightgbm") %>% set_mode("classification")

conf_metrics <- function(y, p, thr) {
  cls <- ifelse(p >= thr, 1, 0)
  tp <- sum(cls == 1 & y == 1); fp <- sum(cls == 1 & y == 0)
  tn <- sum(cls == 0 & y == 0); fn <- sum(cls == 0 & y == 1)
  c(threshold = thr, accuracy = mean(cls == y), sensitivity = tp / (tp + fn),
    specificity = tn / (tn + fp), ppv = tp / (tp + fp), npv = tn / (tn + fn))
}

# 7-day sensitivity
tr7 <- train %>% select(patient_delay_7d, all_of(model_vars)) %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_7d, levels = c(0, 1),
                                          labels = c("No", "Yes"))) %>%
  select(-patient_delay_7d)
te7 <- test %>% select(patient_delay_7d, all_of(model_vars)) %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_7d, levels = c(0, 1),
                                          labels = c("No", "Yes"))) %>%
  select(-patient_delay_7d)
rec7 <- prep(make_rec(tr7), training = tr7)
tr7b <- bake(rec7, new_data = NULL); te7b <- bake(rec7, new_data = te7)
fit7 <- fit(spec_lgb %>% update(mtry = min(27, ncol(tr7b) - 1)),
            patient_delay_14d_clean ~ ., data = tr7b)
p7tr <- predict(fit7, new_data = tr7b, type = "prob")$.pred_Yes
p7te <- predict(fit7, new_data = te7b, type = "prob")$.pred_Yes
y7tr <- as.integer(tr7$patient_delay_14d_clean == "Yes")
y7te <- as.integer(te7$patient_delay_14d_clean == "Yes")
thr7 <- as.numeric(pROC::coords(pROC::roc(y7tr, p7tr, quiet = TRUE), "best",
                                ret = "threshold", best.method = "youden")$threshold[1])
cm7 <- conf_metrics(y7te, p7te, thr7)
auc7 <- as.numeric(pROC::auc(pROC::roc(y7te, p7te, quiet = TRUE)))
pr7 <- pr_auc(tibble(y = factor(y7te, levels = c(0, 1)), p = p7te),
              y, p, event_level = "second")$.estimate
br7 <- mean((p7te - y7te)^2)
seven <- tibble(outcome = "Patient delay >7 days", model = "LightGBM",
                threshold = thr7, event_rate = mean(y7te), roc_auc = auc7,
                pr_auc = pr7, accuracy = cm7["accuracy"],
                sensitivity = cm7["sensitivity"], specificity = cm7["specificity"],
                ppv = cm7["ppv"], npv = cm7["npv"])
print(seven)
write.csv(seven, file.path(outdir, "seven_day_metrics.csv"), row.names = FALSE)

# ensemble
pred_test <- res$pred
pred_test$age_group <- test$age_group
pred_test$户籍地址类别 <- test$户籍地址类别
pl <- pred_test$LightGBM; px <- pred_test$XGBoost
prf <- pred_test$`Random forest`; pen <- pred_test$`Elastic net`
ens_test <- rowMeans(cbind(pl, px, prf, pen))
# train predictions are not stored; refit full LGB etc. too costly; use test threshold 0.50
ens_thr <- 0.50
cm_ens <- conf_metrics(as.integer(pred_test$patient_delay_14d_clean == "Yes"), ens_test, ens_thr)
ens <- tibble(model = "MeanEnsemble", threshold = ens_thr,
              roc_auc = as.numeric(pROC::auc(pROC::roc(as.integer(pred_test$patient_delay_14d_clean == "Yes"), ens_test, quiet = TRUE))),
              pr_auc = pr_auc(tibble(y = pred_test$patient_delay_14d_clean, p = ens_test),
                              y, p, event_level = "second")$.estimate,
              accuracy = cm_ens["accuracy"], sensitivity = cm_ens["sensitivity"],
              specificity = cm_ens["specificity"], ppv = cm_ens["ppv"], npv = cm_ens["npv"])
print(ens)
write.csv(ens, file.path(outdir, "ensemble_metrics.csv"), row.names = FALSE)

# subgroup performance (LightGBM)
subgroup <- function(d, group_label, level) {
  y <- as.integer(d$patient_delay_14d_clean == "Yes")
  p <- d$LightGBM
  if (length(unique(y)) < 2 || nrow(d) < 30) {
    return(tibble(group = group_label, level = level, n = nrow(d),
                  events = sum(y), roc_auc = NA_real_, pr_auc = NA_real_,
                  brier = mean((p - y)^2)))
  }
  tibble(group = group_label, level = level, n = nrow(d), events = sum(y),
         roc_auc = as.numeric(pROC::auc(pROC::roc(y, p, quiet = TRUE))),
         pr_auc = pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = p),
                         y, p, event_level = "second")$.estimate,
         brier = mean((p - y)^2))
}
sub <- bind_rows(
  subgroup(pred_test %>% filter(age_group == "<35"), "Age", "<35"),
  subgroup(pred_test %>% filter(age_group == "35-64"), "Age", "35-64"),
  subgroup(pred_test %>% filter(age_group == ">=65"), "Age", ">=65"),
  subgroup(pred_test %>% filter(gender_clean == "男"), "Sex", "Male"),
  subgroup(pred_test %>% filter(gender_clean == "女"), "Sex", "Female"),
  subgroup(pred_test %>% filter(户籍地址类别 == "本地"), "Residence status", "Local"),
  subgroup(pred_test %>% filter(户籍地址类别 != "本地"), "Residence status", "Migrant")
)
print(sub)
write.csv(sub, file.path(outdir, "subgroup_performance_lightgbm.csv"), row.names = FALSE)

# calibration deciles
cal_tbl <- pred_test %>%
  mutate(y = as.integer(patient_delay_14d_clean == "Yes")) %>%
  pivot_longer(c(LightGBM, XGBoost, `Random forest`, `Elastic net`),
               names_to = "model", values_to = "pred") %>%
  group_by(model) %>%
  mutate(bin = ntile(pred, 10)) %>%
  group_by(model, bin) %>%
  summarise(n = n(), predicted = mean(pred), observed = mean(y), .groups = "drop")
write.csv(cal_tbl, file.path(outdir, "calibration_deciles.csv"), row.names = FALSE)

# Elastic Net coefficients
en_fit <- res$fits$`Elastic net`
coefs <- tidy(en_fit) %>% filter(abs(estimate) > 1e-8) %>% arrange(desc(abs(estimate)))
print(head(coefs, 30))
write.csv(coefs, file.path(outdir, "elasticnet_nonzero_coefficients.csv"), row.names = FALSE)
