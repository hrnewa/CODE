options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
df <- readRDS(file.path(base, "ml_df_final_clean.rds"))
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

d <- df %>%
  mutate(.outcome = factor(patient_delay_7d, levels = c(0, 1), labels = c("No", "Yes"))) %>%
  select(.outcome, all_of(model_vars))
set.seed(123)
sp <- initial_split(d, prop = 0.7, strata = .outcome)
tr <- training(sp)
rec <- recipe(.outcome ~ ., data = tr) %>%
  step_impute_median(all_numeric_predictors()) %>%
  step_impute_mode(all_nominal_predictors()) %>%
  step_log(all_of(geo_vars), offset = 1) %>%
  step_ns(age, deg_free = 4) %>%
  step_other(all_nominal_predictors(), threshold = 0.01) %>%
  step_lencode_glm(all_of(target_encode_vars), outcome = vars(.outcome)) %>%
  step_dummy(all_nominal_predictors(), one_hot = TRUE) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())
recp <- prep(rec, training = tr)
trb <- bake(recp, new_data = NULL)
spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                   learn_rate = 0.008893162, mtry = min(27, ncol(trb) - 1),
                   loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
  set_engine("lightgbm") %>% set_mode("classification")
fit <- fit(spec, .outcome ~ ., data = trb)
p <- predict(fit, new_data = trb, type = "prob")$.pred_Yes
y <- as.integer(tr$.outcome == "Yes")

r <- pROC::roc(y, p, quiet = TRUE)
grid <- as.data.frame(pROC::coords(r, "all", ret = c("threshold", "sensitivity", "specificity"))) %>%
  mutate(j_index = sensitivity + specificity - 1) %>%
  arrange(desc(j_index)) %>%
  slice_head(n = 10)
print(grid)
write.csv(grid, file.path(outdir, "seven_day_threshold_grid.csv"), row.names = FALSE)
te <- testing(sp)
teb <- bake(recp, new_data = te)
pt <- predict(fit, new_data = teb, type = "prob")$.pred_Yes
yt <- as.integer(te$.outcome == "Yes")
thr <- 0.732
cls <- ifelse(pt >= thr, 1, 0)
tp <- sum(cls == 1 & yt == 1); fp <- sum(cls == 1 & yt == 0)
tn <- sum(cls == 0 & yt == 0); fn <- sum(cls == 0 & yt == 1)
out <- tibble(threshold = thr, accuracy = mean(cls == yt),
              sensitivity = tp / (tp + fn), specificity = tn / (tn + fp),
              ppv = tp / (tp + fp), npv = tn / (tn + fn),
              event_rate = mean(yt))
print(out)
write.csv(out, file.path(outdir, "seven_day_metrics_at_0732.csv"), row.names = FALSE)
