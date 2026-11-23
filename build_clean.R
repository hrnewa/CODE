options(width = 200)
suppressPackageStartupMessages({
  library(tidyverse)
})

base <- "D:/橡树湾资料/小论文/结核病延迟ML"

a <- readRDS(file.path(base, "ml_df0412.rds"))
x <- readRDS(file.path(base, "model全数据+区县+路网61342部分膨胀.rds")) %>%
  distinct(...1, .keep_all = TRUE) %>%
  filter(patient_delay >= 0)

stopifnot(nrow(a) == nrow(x))

key <- intersect(names(a), names(x))
key <- setdiff(key, "patient_delay_14d_clean")
mk <- function(d) do.call(paste, c(lapply(d[key], as.character), sep = "|"))
stopifnot(identical(mk(a), mk(x)))

geo <- c("nearest_road_dist", "nearest_road_time", "nearest_straight_dist",
         "avg_road_dist", "avg_road_time", "avg_straight_dist")

clean <- a
clean$patient_delay <- x[["patient_delay"]]
clean$patient_delay_7d <- x[["patient_delay_7d"]]
clean$patient_delay_capped <- pmin(x[["patient_delay"]], 365)
clean$city <- x[["city"]]
clean$province <- ifelse(x[["city"]] == "贵阳", "Guizhou", "Guangxi")
clean$row_id <- x[["...1"]]
clean$patient_id <- x[["patient_id"]]
clean$prefecture <- x[["CITY"]]
clean$address_type <- x[["现地址类型"]]
clean$current_code <- x[["现地址国标"]]
clean$hukou_code <- x[["户籍地址编码"]]
clean$symptom_onset_date <- x[["symptom_onset_date"]]
clean$first_visit_date <- x[["first_visit_date"]]
clean$diagnosis_date <- x[["diagnosis_date"]]
clean$registration_date <- x[["registration_date"]]
clean$insurance_imputed <- is.na(x[["险种类型_simplified"]])
clean$险种类型_final <- x[["险种类型_final"]]
for (g in geo) clean[[g]] <- x[[g]]

code <- ifelse(!is.na(clean$current_code) & clean$current_code != "",
               as.character(clean$current_code),
               as.character(clean$hukou_code))
code <- gsub("[^0-9]", "", code)
clean$county_code <- ifelse(nchar(code) >= 6, substr(code, 1, 6), NA_character_)
sub2 <- suppressWarnings(as.integer(substr(clean$county_code, 5, 6)))
clean$urban_rural <- case_when(
  is.na(sub2) ~ "Unknown",
  sub2 >= 1 & sub2 <= 20 ~ "Urban district",
  sub2 >= 21 & sub2 <= 80 ~ "County",
  sub2 >= 81 & sub2 <= 99 ~ "County-level city",
  TRUE ~ "Unknown"
)
clean$prefecture <- ifelse(is.na(clean$prefecture) | clean$prefecture == "",
                           "Unknown", as.character(clean$prefecture))

# order columns: outcome first, then the model feature set used in the revision
model_vars <- c("gender_clean", "age", "age_squared", "age_group",
                "occupation_group", "ethnicity_group", "is_minority",
                "户籍地址类别", "险种类型_final", "hiv_aids_final", "diabetes_final",
                "symptom_season", "symptom_year", "symptom_month", "is_winter",
                "patient_source_group", "is_referral", "is_direct_visit",
                "symptom_severity_group", "is_asymptomatic_final",
                "has_typical_symptoms_final", "is_key_population_final",
                "重点人群-A.密切接触者_final", "重点人群-D.医务人员_final",
                "重点人群-E.学校托幼机构人员_final", "重点人群-F.监管人员_final",
                "重点人群-G.养殖人员_final",
                "重点人群-H.接尘人员/尘肺病患者_final",
                "重点人群-I.精神病院患者_final", "重点人群-J.养老院居住者_final",
                "重点人群-K.福利院居住者_final",
                "重点人群-L.其他人群聚集场所人员_final", geo)

stopifnot(all(model_vars %in% names(clean)))

clean <- clean %>%
  select(patient_delay_14d_clean, patient_delay, patient_delay_7d,
         patient_delay_capped, all_of(model_vars),
         city, province, row_id, patient_id, prefecture, address_type,
         current_code, hukou_code, county_code, urban_rural,
         symptom_onset_date, first_visit_date, diagnosis_date,
         registration_date, insurance_imputed)

cat("clean cohort:", nrow(clean), "\n")
print(table(clean[["patient_delay_14d_clean"]]))
cat("unique row_id:", n_distinct(clean$row_id), "\n")
cat("negative delay:", sum(clean$patient_delay < 0), " zero:", sum(clean$patient_delay == 0),
    " >365:", sum(clean$patient_delay > 365), "\n")
cat("province:\n"); print(table(clean$province))
cat("city:\n"); print(table(clean$city))
cat("urban_rural:\n"); print(table(clean$urban_rural))
cat("insurance imputed:", sum(clean$insurance_imputed), "\n")
cat("geo NA nearest_road_time:", sum(is.na(clean$nearest_road_time)), "\n")

saveRDS(clean, file.path(base, "ml_df_final_clean.rds"))
write.csv(clean %>% select(row_id, patient_id, city, province, county_code,
                           urban_rural, prefecture,
                           patient_delay, patient_delay_14d_clean),
          file.path(base, "ml_df_final_clean_location.csv"), row.names = FALSE)
cat("saved ml_df_final_clean.rds\n")
