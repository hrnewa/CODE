options(width = 200)
suppressPackageStartupMessages({library(tidyverse); library(pROC)})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
pred <- read.csv(file.path(outdir, "test_predictions.csv"), check.names = FALSE)
df <- readRDS(file.path(base, "ml_df_final_clean.rds")) %>%
  mutate(patient_delay_14d_clean = factor(patient_delay_14d_clean,
                                          levels = c(0, 1), labels = c("No", "Yes")))
set.seed(123)
split <- rsample::initial_split(df, prop = 0.7, strata = patient_delay_14d_clean)
test <- rsample::testing(split)
pred$age_group <- test$age_group
pred$户籍地址类别 <- test$户籍地址类别
pred$y <- as.integer(pred$patient_delay_14d_clean == "Yes")

subgroups <- list(
  list("Age group", "35-64", pred$age_group == "35-64"),
  list("Age group", "<35", pred$age_group == "<35"),
  list("Age group", ">=65", pred$age_group == ">=65"),
  list("Sex", "Female", pred$gender_clean == "女"),
  list("Sex", "Male", pred$gender_clean == "男"),
  list("Residence status", "Local", pred$户籍地址类别 == "本地"),
  list("Residence status", "Migrant", pred$户籍地址类别 != "本地")
)

set.seed(2026)
res <- list()
for (s in subgroups) {
  d <- pred[s[[3]], ]
  y <- d$y; p <- d$LightGBM
  aucv <- as.numeric(pROC::auc(pROC::roc(y, p, quiet = TRUE)))
  boot <- numeric(1000)
  for (b in 1:1000) {
    idx <- sample.int(nrow(d), nrow(d), replace = TRUE)
    if (length(unique(y[idx])) < 2) { boot[b] <- NA; next }
    boot[b] <- as.numeric(pROC::auc(pROC::roc(y[idx], p[idx], quiet = TRUE)))
  }
  res[[length(res) + 1]] <- tibble(
    subgroup_type = s[[1]], level = s[[2]], n = nrow(d), events = sum(y),
    event_rate = mean(y), auc = aucv,
    auc_low = quantile(boot, 0.025, na.rm = TRUE),
    auc_high = quantile(boot, 0.975, na.rm = TRUE)
  )
}
out <- bind_rows(res)
print(out)
write.csv(out, file.path(outdir, "subgroup_performance_with_ci.csv"), row.names = FALSE)
