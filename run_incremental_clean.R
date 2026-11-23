options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
res <- readRDS(file.path(outdir, "clean_model_results.rds"))
recp <- res$recipe
fit_full <- res$fits$LightGBM

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
train_b <- bake(recp, new_data = train %>% select(patient_delay_14d_clean, all_of(model_vars)))
test_b  <- bake(recp, new_data = test  %>% select(patient_delay_14d_clean, all_of(model_vars)))

geo_vars <- c("nearest_road_time", "avg_road_time", "nearest_road_dist",
              "avg_road_dist", "nearest_straight_dist", "avg_straight_dist")
geo_b <- intersect(geo_vars, names(train_b))
cat("geo baked:", paste(geo_b, collapse = ", "), "\n")

p_nogeo <- ncol(train_b) - length(geo_b) - 1
lgb_spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                       learn_rate = 0.008893162, mtry = min(27, p_nogeo),
                       loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
  set_engine("lightgbm") %>% set_mode("classification")
fit_nogeo <- fit(lgb_spec, patient_delay_14d_clean ~ .,
                 data = train_b %>% select(-all_of(geo_b)))
saveRDS(fit_nogeo, file.path(outdir, "fit_nogeo.rds"))

pf <- predict(fit_full, new_data = test_b, type = "prob")$.pred_Yes
pn <- predict(fit_nogeo, new_data = test_b %>% select(-all_of(geo_b)), type = "prob")$.pred_Yes
y <- as.integer(test$patient_delay_14d_clean == "Yes")

auc_fun <- function(y, p) as.numeric(pROC::auc(pROC::roc(y, p, quiet = TRUE)))
pr_fun <- function(y, p) pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = p),
                                y, p, event_level = "second")$.estimate
brier_fun <- function(y, p) mean((p - y)^2)
cal_fun <- function(y, p) {
  lp <- qlogis(pmin(pmax(p, 1e-6), 1 - 1e-6))
  m <- glm(y ~ lp, family = binomial())
  m0 <- glm(y ~ 1, family = binomial(), offset = lp)
  c(intercept = unname(coef(m0)[1]), slope = unname(coef(m)[2]))
}

auc_full <- auc_fun(y, pf); auc_nogeo <- auc_fun(y, pn)
pr_full <- pr_fun(y, pf); pr_nogeo <- pr_fun(y, pn)
br_full <- brier_fun(y, pf); br_nogeo <- brier_fun(y, pn)
cal_full <- cal_fun(y, pf); cal_nogeo <- cal_fun(y, pn)
roc_full <- pROC::roc(y, pf, quiet = TRUE)
roc_nogeo <- pROC::roc(y, pn, quiet = TRUE)
dl <- pROC::roc.test(roc_full, roc_nogeo, method = "delong")

set.seed(42)
B <- 2000; n <- length(y)
d_auc <- d_pr <- d_br <- numeric(B)
for (b in seq_len(B)) {
  idx <- sample.int(n, n, replace = TRUE)
  yb <- y[idx]; pfb <- pf[idx]; pnb <- pn[idx]
  d_auc[b] <- auc_fun(yb, pfb) - auc_fun(yb, pnb)
  d_pr[b]  <- pr_fun(yb, pfb) - pr_fun(yb, pnb)
  d_br[b]  <- brier_fun(yb, pfb) - brier_fun(yb, pnb)
}
ci <- function(x) quantile(x, c(0.025, 0.975), na.rm = TRUE)
inc <- tibble(
  metric = c("ROC-AUC full", "ROC-AUC no geo", "Delta ROC-AUC",
             "PR-AUC full", "PR-AUC no geo", "Delta PR-AUC",
             "Brier full", "Brier no geo", "Delta Brier",
             "Calibration intercept full", "Calibration slope full",
             "Calibration intercept no geo", "Calibration slope no geo"),
  value = c(auc_full, auc_nogeo, auc_full - auc_nogeo,
            pr_full, pr_nogeo, pr_full - pr_nogeo,
            br_full, br_nogeo, br_full - br_nogeo,
            cal_full[1], cal_full[2], cal_nogeo[1], cal_nogeo[2]),
  ci_low = c(NA, NA, ci(d_auc)[1], NA, NA, ci(d_pr)[1], NA, NA, ci(d_br)[1], NA, NA, NA, NA),
  ci_high = c(NA, NA, ci(d_auc)[2], NA, NA, ci(d_pr)[2], NA, NA, ci(d_br)[2], NA, NA, NA, NA),
  p_value = c(NA, NA, dl$p.value, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA)
)
print(inc)
write.csv(inc, file.path(outdir, "incremental_value_same_split.csv"), row.names = FALSE)

# net benefit
nb <- function(p, y, pt) {
  tp <- mean(p >= pt & y == 1); fp <- mean(p >= pt & y == 0)
  tp - fp * pt / (1 - pt)
}
ths <- c(0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.625, 0.70)
nb_tbl <- tibble(
  threshold = ths,
  full = sapply(ths, function(t) nb(pf, y, t)),
  no_geo = sapply(ths, function(t) nb(pn, y, t)),
  treat_all = sapply(ths, function(t) mean(y) - (1 - mean(y)) * t / (1 - t))
)
print(nb_tbl)
write.csv(nb_tbl, file.path(outdir, "net_benefit_comparison.csv"), row.names = FALSE)

# grouped permutation importance (10 reps)
domains <- list(
  Demographics = c("gender_clean", "age", "age_squared", "age_group",
                   "occupation_group", "ethnicity_group", "is_minority"),
  `Household registration & migration` = c("户籍地址类别"),
  `Insurance type` = c("险种类型_final"),
  `Clinical comorbidities` = c("hiv_aids_final", "diabetes_final"),
  `Temporal features` = c("symptom_year", "symptom_month", "symptom_season", "is_winter"),
  `Patient source & care pathway` = c("patient_source_group", "is_referral", "is_direct_visit"),
  Symptoms = c("symptom_severity_group", "is_asymptomatic_final", "has_typical_symptoms_final"),
  `Key population indicators` = c("is_key_population_final", grep("^重点人群", model_vars, value = TRUE)),
  `Geographic accessibility` = geo_vars
)
domains <- lapply(domains, function(v) intersect(v, model_vars))
set.seed(2026)
perm_res <- list()
for (dn in names(domains)) {
  vars <- domains[[dn]]
  if (length(vars) == 0) next
  drops <- numeric(10)
  for (r in 1:10) {
    test_perm <- test
    for (v in vars) test_perm[[v]] <- sample(test_perm[[v]], nrow(test_perm), replace = FALSE)
    pb <- bake(recp, new_data = test_perm %>% select(patient_delay_14d_clean, all_of(model_vars)))
    pp <- predict(fit_full, new_data = pb, type = "prob")$.pred_Yes
    drops[r] <- auc_full - auc_fun(y, pp)
  }
  perm_res[[dn]] <- tibble(domain = dn, n_features = length(vars),
                           mean_drop = mean(drops), low = quantile(drops, 0.025),
                           high = quantile(drops, 0.975))
  cat(dn, "done\n")
}
perm_tbl <- bind_rows(perm_res) %>% arrange(desc(mean_drop))
print(perm_tbl)
write.csv(perm_tbl, file.path(outdir, "domain_permutation_importance.csv"), row.names = FALSE)

# SHAP on final raw-variable model (training data)
cat("Computing SHAP...\n")
X <- as.matrix(train_b %>% select(-patient_delay_14d_clean))
sh <- predict(fit_full$fit, X, type = "contrib")
sh <- as.matrix(sh)
sh <- sh[, 1:ncol(X), drop = FALSE]
colnames(sh) <- colnames(X)
get_domain <- function(fn) {
  if (fn %in% geo_vars) return("Geographic accessibility")
  if (grepl("^age|^gender|^occupation|^ethnicity|^is_minority", fn)) return("Demographics")
  if (grepl("^户籍地址类别", fn)) return("Household registration & migration")
  if (grepl("^险种类型", fn)) return("Insurance type")
  if (grepl("^hiv_aids|^diabetes", fn)) return("Clinical comorbidities")
  if (grepl("^symptom_year|^symptom_month|^symptom_season|^is_winter", fn)) return("Temporal features")
  if (grepl("^patient_source|^is_referral|^is_direct", fn)) return("Patient source & care pathway")
  if (grepl("^symptom_severity|^is_asymptomatic|^has_typical", fn)) return("Symptoms")
  if (grepl("^重点人群|^is_key_population", fn)) return("Key population indicators")
  return("Other")
}
dom <- sapply(colnames(sh), get_domain)
mean_abs <- colMeans(abs(sh))
feat <- tibble(feature = colnames(sh), domain = dom,
               mean_abs_shap = as.numeric(mean_abs)) %>%
  arrange(desc(mean_abs_shap))
domtbl <- feat %>% group_by(domain) %>%
  summarise(mean_abs_shap = sum(mean_abs_shap), n_features = n(), .groups = "drop") %>%
  mutate(percentage = 100 * mean_abs_shap / sum(mean_abs_shap)) %>%
  arrange(desc(mean_abs_shap))
print(domtbl)
write.csv(feat, file.path(outdir, "shap_feature_importance_rawmodel.csv"), row.names = FALSE)
write.csv(domtbl, file.path(outdir, "shap_domain_importance_rawmodel.csv"), row.names = FALSE)
saveRDS(sh, file.path(outdir, "shap_values_train_rawmodel.rds"))

saveRDS(list(inc = inc, nb = nb_tbl, perm = perm_tbl, shap_domain = domtbl,
             shap_feature = feat, pred_full = pf, pred_nogeo = pn, y = y),
        file.path(outdir, "incremental_results.rds"))
cat("Saved incremental outputs to", outdir, "\n")
