options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")

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

fit_compare <- function(label, extra_vars = NULL, drop_geo = FALSE) {
  vars <- model_vars
  if (drop_geo) vars <- setdiff(vars, geo_vars)
  vars <- unique(c(vars, extra_vars))
  tr <- train %>% select(patient_delay_14d_clean, all_of(vars))
  te <- test  %>% select(patient_delay_14d_clean, all_of(vars))
  rec <- recipe(patient_delay_14d_clean ~ ., data = tr) %>%
    step_impute_median(all_numeric_predictors()) %>%
    step_impute_mode(all_nominal_predictors()) %>%
    step_log(all_of(intersect(geo_vars, vars)), offset = 1) %>%
    step_ns(age, deg_free = 4) %>%
    step_other(all_nominal_predictors(), threshold = 0.01) %>%
    step_lencode_glm(all_of(intersect(target_encode_vars, vars)),
                     outcome = vars(patient_delay_14d_clean)) %>%
    step_dummy(all_nominal_predictors(), one_hot = TRUE) %>%
    step_zv(all_predictors()) %>%
    step_normalize(all_numeric_predictors())
  recp <- prep(rec, training = tr)
  trb <- bake(recp, new_data = NULL); teb <- bake(recp, new_data = te)
  p <- ncol(trb) - 1
  spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                     learn_rate = 0.008893162, mtry = min(27, p),
                     loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
    set_engine("lightgbm") %>% set_mode("classification")
  fit <- fit(spec, patient_delay_14d_clean ~ ., data = trb)
  pred <- predict(fit, new_data = teb, type = "prob")$.pred_Yes
  y <- as.integer(te$patient_delay_14d_clean == "Yes")
  aucv <- as.numeric(pROC::auc(pROC::roc(y, pred, quiet = TRUE)))
  prv <- pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = pred),
                y, p, event_level = "second")$.estimate
  lp <- qlogis(pmin(pmax(pred, 1e-6), 1 - 1e-6))
  m <- glm(y ~ lp, family = binomial())
  m0 <- glm(y ~ 1, family = binomial(), offset = lp)
  tibble(model = label, n_predictors = p, roc_auc = aucv, pr_auc = prv,
         brier = mean((pred - y)^2),
         cal_intercept = unname(coef(m0)[1]), cal_slope = unname(coef(m)[2]))
}

comp <- bind_rows(
  fit_compare("Full model (6 geographic variables)"),
  fit_compare("No geographic domain", drop_geo = TRUE),
  fit_compare("Prefecture identifier instead of geography", extra_vars = "prefecture", drop_geo = TRUE),
  fit_compare("Urban/rural proxy instead of geography", extra_vars = "urban_rural", drop_geo = TRUE),
  fit_compare("Prefecture + urban/rural instead of geography", extra_vars = c("prefecture", "urban_rural"), drop_geo = TRUE),
  fit_compare("City identifier instead of geography", extra_vars = "city", drop_geo = TRUE)
)
print(comp)
write.csv(comp, file.path(outdir, "location_comparator_models.csv"), row.names = FALSE)

# key-population unknown by year and province
key_cols <- grep("^重点人群-.*_final$", names(df), value = TRUE)
kp <- df %>%
  mutate(across(all_of(key_cols), ~ .x == "未知", .names = "{.col}_unknown")) %>%
  group_by(symptom_year, province) %>%
  summarise(n = n(),
            across(all_of(paste0(key_cols, "_unknown")), sum),
            .groups = "drop")
print(kp)
write.csv(kp, file.path(outdir, "key_population_unknown_by_year_province.csv"), row.names = FALSE)

# identical unknown counts across subtypes
unk <- df %>% summarise(across(all_of(key_cols), ~ sum(.x == "未知")))
print(unk)
write.csv(t(unk), file.path(outdir, "key_population_unknown_totals.csv"), row.names = TRUE)

# insurance imputation
ins <- df %>%
  group_by(province, city, insurance_imputed, 险种类型_final) %>%
  summarise(n = n(), .groups = "drop") %>%
  arrange(desc(n))
print(ins)
write.csv(ins, file.path(outdir, "insurance_imputation_counts.csv"), row.names = FALSE)

ins_sum <- df %>%
  group_by(province) %>%
  summarise(n = n(), imputed = sum(insurance_imputed),
            imputed_pct = 100 * mean(insurance_imputed), .groups = "drop")
print(ins_sum)
write.csv(ins_sum, file.path(outdir, "insurance_imputation_summary.csv"), row.names = FALSE)
