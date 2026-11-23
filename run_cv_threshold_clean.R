options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC)
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
set.seed(123)
split <- initial_split(df, prop = 0.7, strata = patient_delay_14d_clean)
train <- training(split); test <- testing(split)
train_b <- bake(res$recipe, new_data = train %>% select(patient_delay_14d_clean, all_of(model_vars)))
test_b <- bake(res$recipe, new_data = test %>% select(patient_delay_14d_clean, all_of(model_vars)))

spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                   learn_rate = 0.008893162, mtry = 27,
                   loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
  set_engine("lightgbm") %>% set_mode("classification")

set.seed(456)
folds <- vfold_cv(train_b, v = 5, strata = patient_delay_14d_clean)
oof <- list()
for (i in seq_along(folds$splits)) {
  sp <- folds$splits[[i]]
  tr <- analysis(sp); te <- assessment(sp)
  fit <- fit(spec %>% update(mtry = min(27, ncol(tr) - 1)), patient_delay_14d_clean ~ ., data = tr)
  pr <- predict(fit, new_data = te, type = "prob")$.pred_Yes
  oof[[i]] <- tibble(obs = te$patient_delay_14d_clean, pred = pr)
  cat("fold", i, "done\n")
}
oof <- bind_rows(oof)
y <- as.integer(oof$obs == "Yes")
thr <- as.numeric(pROC::coords(pROC::roc(y, oof$pred, quiet = TRUE), "best",
                               ret = "threshold", best.method = "youden")$threshold[1])
cat("CV Youden threshold:", thr, "\n")

pred <- predict(res$fits$LightGBM, new_data = test_b, type = "prob")$.pred_Yes
yte <- as.integer(test$patient_delay_14d_clean == "Yes")
cls <- ifelse(pred >= thr, 1, 0)
tp <- sum(cls == 1 & yte == 1); fp <- sum(cls == 1 & yte == 0)
tn <- sum(cls == 0 & yte == 0); fn <- sum(cls == 0 & yte == 1)
out <- tibble(threshold = thr, accuracy = mean(cls == yte),
              sensitivity = tp / (tp + fn), specificity = tn / (tn + fp),
              ppv = tp / (tp + fp), npv = tn / (tn + fn))
print(out)
write.csv(out, file.path(outdir, "cv_threshold_metrics.csv"), row.names = FALSE)
