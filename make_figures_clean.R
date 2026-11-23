options(width = 200)
suppressPackageStartupMessages({
  library(tidymodels); library(tidyverse); library(bonsai)
  library(lightgbm); library(embed); library(pROC); library(ggplot2)
  library(patchwork); library(pdp)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
res <- readRDS(file.path(outdir, "clean_model_results.rds"))
pred <- read.csv(file.path(outdir, "test_predictions.csv"), check.names = FALSE)
y <- as.integer(pred$patient_delay_14d_clean == "Yes")

# ROC curves
models <- c("LightGBM", "XGBoost", "Random forest", "Elastic net")
roc_list <- lapply(models, function(m) {
  r <- pROC::roc(y, pred[[m]], quiet = TRUE)
  data.frame(model = m, specificity = r$specificities, sensitivity = r$sensitivities)
})
names(roc_list) <- models
roc_df <- bind_rows(roc_list)
ens <- rowMeans(pred[, models])
r_ens <- pROC::roc(y, ens, quiet = TRUE)
roc_df <- bind_rows(roc_df, data.frame(model = "Mean ensemble",
                                       specificity = r_ens$specificities,
                                       sensitivity = r_ens$sensitivities))
auc_lab <- c(
  LightGBM = sprintf("LightGBM (AUC %.3f)", as.numeric(pROC::auc(pROC::roc(y, pred$LightGBM, quiet = TRUE)))),
  XGBoost = sprintf("XGBoost (AUC %.3f)", as.numeric(pROC::auc(pROC::roc(y, pred$XGBoost, quiet = TRUE)))),
  `Random forest` = sprintf("Random forest (AUC %.3f)", as.numeric(pROC::auc(pROC::roc(y, pred$`Random forest`, quiet = TRUE)))),
  `Elastic net` = sprintf("Elastic net (AUC %.3f)", as.numeric(pROC::auc(pROC::roc(y, pred$`Elastic net`, quiet = TRUE)))),
  `Mean ensemble` = sprintf("Mean ensemble (AUC %.3f)", as.numeric(pROC::auc(r_ens)))
)
roc_df$model <- factor(roc_df$model, levels = names(auc_lab), labels = auc_lab)
p_roc <- ggplot(roc_df, aes(x = 1 - specificity, y = sensitivity, colour = model)) +
  geom_abline(slope = 1, intercept = 0, colour = "grey70", linetype = 2) +
  geom_path(linewidth = 0.9) +
  scale_colour_manual(values = c("#D7191C", "#FDAE61", "#2C7BB6", "#ABD9E9", "grey30")) +
  labs(x = "1 - Specificity", y = "Sensitivity", colour = NULL) +
  theme_bw(base_size = 11) +
  theme(legend.position = c(0.98, 0.02), legend.justification = c(1, 0),
        legend.background = element_rect(fill = "white", colour = NA))
ggsave(file.path(outdir, "Figure2_ROC.png"), p_roc, width = 6.5, height = 5.5, dpi = 300)

# Calibration
cal <- read.csv(file.path(outdir, "calibration_deciles.csv"), check.names = FALSE)
cal_lgb <- cal %>% filter(model == "LightGBM")
cal_xgb <- cal %>% filter(model == "XGBoost")
p_cal <- ggplot() +
  geom_abline(slope = 1, intercept = 0, colour = "grey70", linetype = 2) +
  geom_line(data = cal_lgb, aes(x = predicted, y = observed, colour = "LightGBM"),
            linewidth = 0.9) +
  geom_point(data = cal_lgb, aes(x = predicted, y = observed, colour = "LightGBM"),
             size = 2.2) +
  geom_line(data = cal_xgb, aes(x = predicted, y = observed, colour = "XGBoost"),
            linewidth = 0.8, linetype = 3) +
  geom_point(data = cal_xgb, aes(x = predicted, y = observed, colour = "XGBoost"),
             size = 1.8, shape = 1) +
  scale_colour_manual(values = c(LightGBM = "#D7191C", XGBoost = "#2C7BB6"),
                      name = NULL) +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
  labs(x = "Predicted probability", y = "Observed proportion") +
  theme_bw(base_size = 11) +
  theme(legend.position = c(0.02, 0.98), legend.justification = c(0, 1),
        legend.background = element_rect(fill = "white", colour = NA))
ggsave(file.path(outdir, "Figure3_calibration.png"), p_cal, width = 5.5, height = 5.2, dpi = 300)

# DCA
inc <- readRDS(file.path(outdir, "incremental_results.rds"))
pf <- inc$pred_full; pn <- inc$pred_nogeo; yy <- inc$y
ths <- seq(0.05, 0.85, by = 0.005)
nb <- function(p, pt) {
  tp <- mean(p >= pt & yy == 1); fp <- mean(p >= pt & yy == 0)
  tp - fp * pt / (1 - pt)
}
dca <- tibble(
  threshold = ths,
  Full = sapply(ths, function(t) nb(pf, t)),
  `Without geography` = sapply(ths, function(t) nb(pn, t)),
  `Treat all` = sapply(ths, function(t) mean(yy) - (1 - mean(yy)) * t / (1 - t))
) %>%
  pivot_longer(-threshold, names_to = "strategy", values_to = "net_benefit")
p_dca <- ggplot(dca, aes(x = threshold, y = net_benefit, colour = strategy, linetype = strategy)) +
  geom_hline(yintercept = 0, colour = "grey70") +
  geom_line(linewidth = 0.9) +
  scale_colour_manual(values = c(Full = "#D7191C", `Without geography` = "#2C7BB6",
                                 `Treat all` = "grey30"), name = NULL) +
  scale_linetype_manual(values = c(Full = 1, `Without geography` = 2, `Treat all` = 3), name = NULL) +
  coord_cartesian(ylim = c(-0.05, 0.65)) +
  labs(x = "Threshold probability", y = "Net benefit") +
  theme_bw(base_size = 11) +
  theme(legend.position = c(0.98, 0.98), legend.justification = c(1, 1),
        legend.background = element_rect(fill = "white", colour = NA))
ggsave(file.path(outdir, "FigureS2_DCA.png"), p_dca, width = 6.5, height = 5.2, dpi = 300)

# SHAP values and baked training data
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
train <- training(split)
train_b <- bake(res$recipe, new_data = train %>% select(patient_delay_14d_clean, all_of(model_vars)))
X <- train_b %>% select(-patient_delay_14d_clean)
sh <- readRDS(file.path(outdir, "shap_values_train_rawmodel.rds"))
stopifnot(identical(colnames(sh), colnames(X)))

feat <- read.csv(file.path(outdir, "shap_feature_importance_rawmodel.csv"), check.names = FALSE)
domtbl <- read.csv(file.path(outdir, "shap_domain_importance_rawmodel.csv"), check.names = FALSE)

label_map <- c(
  "symptom_year" = "Symptom onset year",
  "symptom_month" = "Symptom onset month",
  "occupation_group" = "Occupation",
  "is_referral" = "Referral",
  "avg_road_dist" = "Average road distance",
  "avg_road_time" = "Average road travel time",
  "nearest_road_time" = "Nearest road travel time",
  "nearest_road_dist" = "Nearest road distance",
  "nearest_straight_dist" = "Nearest straight-line distance",
  "avg_straight_dist" = "Average straight-line distance",
  "age_squared" = "Age (squared)",
  "has_typical_symptoms_final" = "Typical symptoms",
  "户籍地址类别" = "Residence status",
  "patient_source_group" = "Patient source",
  "is_direct_visit" = "Direct visit",
  "is_asymptomatic_final" = "Asymptomatic",
  "symptom_severity_group" = "Symptom severity",
  "is_minority" = "Ethnic minority"
)
top <- feat %>% slice_head(n = 18)
clean_label <- function(x) {
  if (x %in% names(label_map)) return(unname(label_map[x]))
  if (grepl("^age_ns", x)) return(paste0("Age spline ", sub(".*_", "", x)))
  lv_map <- c("是" = "Yes", "否" = "No", "未知" = "Unknown")
  if (grepl("^重点人群-", x)) {
    code <- sub("^重点人群-([A-L])\\..*$", "\\1", x)
    lv <- sub(".*_final_", "", x)
    pop <- c(A = "Close contact", D = "Health-care worker",
             E = "School/kindergarten personnel", F = "Custodial personnel",
             G = "Livestock worker", H = "Dust-exposed worker",
             I = "Psychiatric-hospital patient", J = "Nursing-home resident",
             K = "Welfare-institution resident", L = "Other congregate setting")
    return(paste0(pop[[code]], ": ", lv_map[[lv]]))
  }
  if (grepl("^diabetes_final_", x)) {
    lv <- sub(".*_final_", "", x)
    return(paste0("Diabetes: ", lv_map[[lv]]))
  }
  if (grepl("^hiv_aids_final_", x)) {
    lv <- sub(".*_final_", "", x)
    return(paste0("HIV/AIDS: ", lv_map[[lv]]))
  }
  x
}
top$label <- vapply(top$feature, clean_label, character(1))

set.seed(7)
idx <- sample(seq_len(nrow(X)), min(4000, nrow(X)))
long <- as_tibble(sh[idx, top$feature, drop = FALSE]) %>%
  mutate(.row = row_number()) %>%
  pivot_longer(-.row, names_to = "feature", values_to = "shap")
vals <- as_tibble(X[idx, top$feature, drop = FALSE]) %>%
  mutate(.row = row_number()) %>%
  pivot_longer(-.row, names_to = "feature", values_to = "value")
long <- left_join(long, vals, by = c(".row", "feature")) %>%
  left_join(top %>% select(feature, label, mean_abs_shap), by = "feature") %>%
  group_by(feature) %>%
  mutate(value_scaled = (value - min(value, na.rm = TRUE)) /
           (max(value, na.rm = TRUE) - min(value, na.rm = TRUE) + 1e-12)) %>%
  ungroup() %>%
  mutate(label = factor(label, levels = rev(top$label)))

p_shap <- ggplot(long, aes(x = shap, y = label, colour = value_scaled)) +
  geom_vline(xintercept = 0, colour = "grey70", linewidth = 0.3) +
  geom_jitter(height = 0.18, size = 0.45, alpha = 0.55) +
  scale_colour_gradientn(colours = c("#2C7BB6", "#ABD9E9", "#FDAE61", "#D7191C"),
                         name = "Feature value\n(within-feature scale)") +
  labs(x = "SHAP value (log-odds)", y = NULL) +
  theme_bw(base_size = 11) +
  theme(panel.grid.major.y = element_blank(),
        legend.position = "right")
ggsave(file.path(outdir, "Figure4_SHAP_beeswarm.png"), p_shap, width = 9, height = 7, dpi = 300)

# Variable importance
top20 <- feat %>% slice_head(n = 20)
top20$label <- vapply(top20$feature, clean_label, character(1))
top20 <- top20 %>% mutate(is_geo = domain == "Geographic accessibility",
                          label = factor(label, levels = rev(label)))
p_vi <- ggplot(top20, aes(x = mean_abs_shap, y = label)) +
  geom_segment(aes(x = 0, xend = mean_abs_shap, yend = label),
               colour = "grey75", linewidth = 0.5) +
  geom_point(aes(colour = is_geo), size = 2.6) +
  scale_colour_manual(values = c(`TRUE` = "#D7191C", `FALSE` = "#2C7BB6"),
                      guide = "none") +
  labs(x = "Mean |SHAP| (log-odds)", y = NULL) +
  theme_bw(base_size = 11) +
  theme(panel.grid.major.y = element_blank())
ggsave(file.path(outdir, "FigureS3_variable_importance.png"), p_vi, width = 9, height = 7, dpi = 300)

# Domain SHAP
domtbl <- domtbl %>% mutate(domain = factor(domain, levels = rev(domain)),
                            is_geo = domain == "Geographic accessibility")
p_dom <- ggplot(domtbl, aes(x = percentage, y = domain)) +
  geom_col(aes(fill = is_geo), width = 0.68) +
  geom_text(aes(label = sprintf("%.1f%%", percentage)), hjust = -0.12, size = 3.6) +
  scale_fill_manual(values = c(`TRUE` = "#D7191C", `FALSE` = "#2C7BB6"), guide = "none") +
  scale_x_continuous(expand = expansion(mult = c(0, 0.22))) +
  labs(x = "Percentage of total mean |SHAP|", y = NULL) +
  theme_bw(base_size = 11) +
  theme(panel.grid.major.y = element_blank())
ggsave(file.path(outdir, "FigureS8_domain_shap.png"), p_dom, width = 8, height = 5.5, dpi = 300)

# PDP/ICE
pred_fun <- function(object, newdata) {
  b <- bake(res$recipe, new_data = newdata)
  as.numeric(predict(res$fits$LightGBM, new_data = b, type = "prob")$.pred_Yes)
}
set.seed(42)
idx <- sample(seq_len(nrow(df)), min(1200, nrow(df)))
Xsample <- df[idx, c("patient_delay_14d_clean", model_vars)]
make_pdp <- function(v, lab, xmax) {
  pd <- pdp::partial(object = NULL, pred.var = v, train = Xsample,
                     pred.fun = pred_fun, ice = TRUE, center = FALSE,
                     grid.resolution = 25)
  ggplot(pd, aes(x = .data[[v]], y = yhat)) +
    geom_line(aes(group = yhat.id), alpha = 0.03, colour = "grey50", linewidth = 0.3) +
    stat_summary(fun = mean, geom = "line", colour = "#D7191C", linewidth = 1.3) +
    coord_cartesian(xlim = c(0, xmax)) +
    labs(x = lab, y = "Predicted probability of delayed entry") +
    theme_bw(base_size = 11)
}
p1 <- make_pdp("nearest_road_time", "Nearest road-network travel time (seconds)", 10000)
p2 <- make_pdp("avg_road_dist", "Average road-network distance (metres)", 100000)
p_pdp <- p1 + p2 + plot_annotation(tag_levels = "A") + plot_layout(axes = "collect")
ggsave(file.path(outdir, "FigureS9_PDP.png"), p_pdp, width = 12, height = 5, dpi = 300)

cat("Saved figures to", outdir, "\n")
