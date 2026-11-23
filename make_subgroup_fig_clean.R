suppressPackageStartupMessages({library(tidyverse); library(ggplot2)})
base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
d <- read.csv(file.path(outdir, "subgroup_performance_with_ci.csv"), check.names = FALSE) %>%
  mutate(label = paste0(subgroup_type, ": ", level),
         label = factor(label, levels = rev(label)))
p <- ggplot(d, aes(x = auc, y = label)) +
  geom_vline(xintercept = 0.699, linetype = 2, colour = "grey50") +
  geom_errorbarh(aes(xmin = auc_low, xmax = auc_high), height = 0.2, colour = "#2C7BB6") +
  geom_point(size = 2.4, colour = "#D7191C") +
  scale_x_continuous(limits = c(0.63, 0.73)) +
  labs(x = "ROC-AUC (95% CI)", y = NULL) +
  theme_bw(base_size = 11) +
  theme(panel.grid.major.y = element_blank())
ggsave(file.path(outdir, "FigureS7_subgroup.png"), p, width = 8, height = 4.2, dpi = 300)
cat("saved subgroup figure\n")
