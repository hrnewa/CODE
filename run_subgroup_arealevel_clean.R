options(width = 200)
suppressPackageStartupMessages({
  library(tidyverse); library(pROC); library(yardstick)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")

pred <- read.csv(file.path(outdir, "test_predictions.csv"), check.names = FALSE) %>%
  mutate(y = as.integer(patient_delay_14d_clean == "Yes"))

models <- c("LightGBM", "XGBoost", "Random forest", "Elastic net")

metric_group <- function(d, model, group_label, group_value) {
  p <- d[[model]]
  y <- d$y
  if (length(unique(y)) < 2 || nrow(d) < 30) {
    return(tibble(model = model, group = group_label, level = group_value,
                  n = nrow(d), events = sum(y), event_rate = mean(y),
                  roc_auc = NA_real_, pr_auc = NA_real_, brier = mean((p - y)^2),
                  cal_intercept = NA_real_, cal_slope = NA_real_))
  }
  aucv <- as.numeric(pROC::auc(pROC::roc(y, p, quiet = TRUE)))
  prv <- pr_auc(tibble(y = factor(y, levels = c(0, 1)), p = p),
                y, p, event_level = "second")$.estimate
  lp <- qlogis(pmin(pmax(p, 1e-6), 1 - 1e-6))
  m <- glm(y ~ lp, family = binomial())
  m0 <- glm(y ~ 1, family = binomial(), offset = lp)
  tibble(model = model, group = group_label, level = group_value,
         n = nrow(d), events = sum(y), event_rate = mean(y),
         roc_auc = aucv, pr_auc = prv, brier = mean((p - y)^2),
         cal_intercept = unname(coef(m0)[1]), cal_slope = unname(coef(m)[2]))
}

res <- list()
for (m in models) {
  res[[length(res) + 1]] <- metric_group(pred, m, "Province", "Overall")
  for (g in c("Guangxi", "Guizhou")) {
    d <- pred %>% filter(province == g)
    res[[length(res) + 1]] <- metric_group(d, m, "Province", g)
  }
  for (g in c("南宁", "柳州", "贵阳")) {
    d <- pred %>% filter(city == g)
    res[[length(res) + 1]] <- metric_group(d, m, "City", g)
  }
  for (g in c("Urban district", "County", "County-level city")) {
    d <- pred %>% filter(province == "Guangxi", urban_rural == g)
    res[[length(res) + 1]] <- metric_group(d, m, "Urban/rural (Guangxi)", g)
  }
}
sub <- bind_rows(res)
print(sub %>% filter(model == "LightGBM"))
write.csv(sub, file.path(outdir, "subgroup_performance.csv"), row.names = FALSE)

# area-level: prefecture and county, LightGBM
area_one <- function(d, group_label) {
  d %>%
    group_by(level = .data[[group_label]]) %>%
    summarise(n = n(), events = sum(y), observed = mean(y),
              predicted = mean(LightGBM), .groups = "drop") %>%
    mutate(group = group_label, difference = predicted - observed)
}
pref <- area_one(pred, "prefecture") %>% arrange(desc(n))
cnt  <- area_one(pred %>% filter(!is.na(county_code)), "county_code") %>% arrange(desc(n))
print(pref)
print(head(cnt, 30))
write.csv(pref, file.path(outdir, "area_level_prefecture.csv"), row.names = FALSE)
write.csv(cnt, file.path(outdir, "area_level_county.csv"), row.names = FALSE)

# area-level calibration metrics (weighted correlation and regression)
area_cal <- function(d, label) {
  if (nrow(d) < 5) return(NULL)
  m <- lm(observed ~ predicted, data = d, weights = n)
  tibble(group = label, n_areas = nrow(d),
         weighted_r = cor(d$predicted, d$observed),
         slope = unname(coef(m)[2]), intercept = unname(coef(m)[1]),
         mean_abs_diff = weighted.mean(abs(d$difference), d$n))
}
area_tbl <- bind_rows(
  area_cal(pref %>% filter(n >= 100), "Prefecture (n>=100)"),
  area_cal(cnt %>% filter(n >= 200), "County (n>=200, Guangxi)")
)
print(area_tbl)
write.csv(area_tbl, file.path(outdir, "area_level_calibration.csv"), row.names = FALSE)
