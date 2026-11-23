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

run_one <- function(data, label, outcome = c("patient_delay_14d_clean", "patient_delay_7d"),
                    drop_vars = NULL) {
  outcome <- match.arg(outcome)
  d <- data
  if (outcome == "patient_delay_14d_clean") {
    d$.outcome <- factor(d$patient_delay_14d_clean, levels = c(0, 1), labels = c("No", "Yes"))
  } else {
    d$.outcome <- factor(d$patient_delay_7d, levels = c(0, 1), labels = c("No", "Yes"))
  }
  vars <- setdiff(model_vars, drop_vars)
  d <- d %>% select(.outcome, all_of(vars))
  set.seed(123)
  sp <- initial_split(d, prop = 0.7, strata = .outcome)
  tr <- training(sp); te <- testing(sp)
  rec <- recipe(.outcome ~ ., data = tr) %>%
    step_impute_median(all_numeric_predictors()) %>%
    step_impute_mode(all_nominal_predictors()) %>%
    step_log(all_of(intersect(geo_vars, vars)), offset = 1) %>%
    step_ns(age, deg_free = 4) %>%
    step_other(all_nominal_predictors(), threshold = 0.01) %>%
    step_lencode_glm(all_of(intersect(target_encode_vars, vars)),
                     outcome = vars(.outcome)) %>%
    step_dummy(all_nominal_predictors(), one_hot = TRUE) %>%
    step_zv(all_predictors()) %>%
    step_normalize(all_numeric_predictors())
  recp <- prep(rec, training = tr)
  trb <- bake(recp, new_data = NULL)
  teb <- bake(recp, new_data = te)
  p <- ncol(trb) - 1
  spec <- boost_tree(trees = 1445, tree_depth = 8, min_n = 36,
                     learn_rate = 0.008893162, mtry = min(27, p),
                     loss_reduction = 4.678094e-7, sample_size = 0.979231) %>%
    set_engine("lightgbm") %>% set_mode("classification")
  fit <- fit(spec, .outcome ~ ., data = trb)
  pred <- predict(fit, new_data = teb, type = "prob")$.pred_Yes
  y <- as.integer(te$.outcome == "Yes")
  aucv <- as.numeric(pROC::auc(pROC::roc(y, pred, quiet = TRUE)))
  prv <- pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = pred),
                y, p, event_level = "second")$.estimate
  br <- mean((pred - y)^2)
  cal <- {
    lp <- qlogis(pmin(pmax(pred, 1e-6), 1 - 1e-6))
    m <- glm(y ~ lp, family = binomial())
    m0 <- glm(y ~ 1, family = binomial(), offset = lp)
    c(unname(coef(m0)[1]), unname(coef(m)[2]))
  }
  tibble(analysis = label, outcome = outcome, n = nrow(d),
         events = sum(d$.outcome == "Yes"), event_rate = mean(d$.outcome == "Yes"),
         test_n = nrow(te), test_events = sum(te$.outcome == "Yes"),
         roc_auc = aucv, pr_auc = prv, brier = br,
         cal_intercept = cal[1], cal_slope = cal[2])
}

dup_drop <- c("age_squared", "age_group", "is_minority", "symptom_month",
              "is_winter", "is_referral", "is_direct_visit", "is_asymptomatic_final")

res <- list()
res[[1]] <- run_one(df, "Main analysis (14-day outcome)")
res[[2]] <- run_one(df %>% filter(patient_delay_capped > 0), "Excluding zero-delay records")
res[[3]] <- run_one(df %>% filter(patient_delay_capped < 365), "Excluding delays >=365 days")
res[[4]] <- run_one(df, "Without symptom-onset year", drop_vars = "symptom_year")
res[[5]] <- run_one(df, "Deduplicated encodings", drop_vars = dup_drop)
res[[6]] <- run_one(df, "7-day outcome", outcome = "patient_delay_7d")
out <- bind_rows(res)
print(out)
write.csv(out, file.path(outdir, "sensitivity_analyses.csv"), row.names = FALSE)
saveRDS(out, file.path(outdir, "sensitivity_analyses.rds"))
