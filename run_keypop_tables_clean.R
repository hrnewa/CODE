options(width = 200)
suppressPackageStartupMessages({library(tidyverse)})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"
outdir <- file.path(base, "ml_results/revision_clean")
df <- readRDS(file.path(base, "ml_df_final_clean.rds"))
key_cols <- grep("^重点人群-.*_final$", names(df), value = TRUE)

df2 <- df %>%
  mutate(any_unknown = rowSums(across(all_of(key_cols), ~ .x == "未知")) > 0)

by_year <- df2 %>%
  filter(symptom_year >= 2018, symptom_year <= 2024) %>%
  group_by(symptom_year, province) %>%
  summarise(n = n(), any_unknown = sum(any_unknown),
            close_contact = sum(`重点人群-A.密切接触者_final` == "未知"),
            custodial = sum(`重点人群-F.监管人员_final` == "未知"),
            livestock = sum(`重点人群-G.养殖人员_final` == "未知"),
            nursing_home = sum(`重点人群-J.养老院居住者_final` == "未知"),
            .groups = "drop")
print(by_year)
write.csv(by_year, file.path(outdir, "keypop_unknown_by_year_province_compact.csv"), row.names = FALSE)

subtype <- df2 %>%
  summarise(across(all_of(key_cols), ~ sum(.x == "未知"))) %>%
  pivot_longer(everything(), names_to = "subtype", values_to = "unknown_n") %>%
  mutate(pct = 100 * unknown_n / nrow(df2))
print(subtype)
write.csv(subtype, file.path(outdir, "keypop_unknown_subtype_totals.csv"), row.names = FALSE)

subtype_prov <- df2 %>%
  group_by(province) %>%
  summarise(across(all_of(key_cols), ~ sum(.x == "未知")), .groups = "drop") %>%
  pivot_longer(-province, names_to = "subtype", values_to = "unknown_n") %>%
  pivot_wider(names_from = province, values_from = unknown_n)
print(subtype_prov)
write.csv(subtype_prov, file.path(outdir, "keypop_unknown_subtype_by_province.csv"), row.names = FALSE)
