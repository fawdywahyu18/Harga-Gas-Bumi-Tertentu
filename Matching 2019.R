library(WeightIt)
library(readxl)
library(dplyr)
library(cobalt)
library(lmtest)
library(sandwich)
library(stargazer)
library(Matching)
library(MatchIt)
library(optmatch)
library(quickmatch)
library(writexl)

# Load data
wd = ''
wd2 = ''
mac_wd = ''
setwd(wd)
df_2019 = read_excel('Data Export/IBS 2019 Selected.xlsx')

# Extract column name
column_names = colnames(df_2019)
kolom_terpilih = c('Kode Klasifikasi', 'Total Pekerja', 'Total Upah', 'Tenaga Listrik',
                   'Nilai Produksi', 'Total Volume Bahan Bakar', 'Sumber Modal Utama',
                   'Tujuan Penjualan Utama', 'Persentase Nilai Gas Bumi', 'Nominal GVA')
df_terpilih = df_2019[kolom_terpilih]
df_terpilih$`Sumber Modal Utama` = as.factor(df_terpilih$`Sumber Modal Utama`)
df_terpilih$`Tujuan Penjualan Utama` = as.factor(df_terpilih$`Tujuan Penjualan Utama`)
kolom_baru = c('kode_klasifikasi', 'total_pekerja', 'total_upah', 'tenaga_listrik',
               'nilai_produksi', 'total_energi', 'modal_utama', 'penjualan_utama',
               'treatment', 'outcome')
colnames(df_terpilih) = kolom_baru
# df_terpilih$kode_klasifikasi = as.factor(df_terpilih$kode_klasifikasi)

# Berdasarkan perpres tahun 2016, hanya 6 industri yang mendapatkan Harga Tertentu Gas Bumi
df_terpilih2 = df_terpilih %>%
  filter(kode_klasifikasi==21 | kode_klasifikasi==24 | kode_klasifikasi==23 | kode_klasifikasi==22 | kode_klasifikasi==20)

# Outcome variable
ln_outcome = log(df_terpilih$outcome)
by_kbli = df_terpilih %>%
  group_by(kode_klasifikasi) %>%
  summarise(gva_industri = sum(outcome))
df_merge = merge(df_terpilih, by_kbli, by='kode_klasifikasi')
df_merge$kontribusi_gva = df_merge$outcome/df_merge$gva_industri
df_merge$log_gva = ln_outcome

# Demeaning process
df_merge$demean_ln_gva = df_merge$log_gva - mean(df_merge$log_gva)
df_merge$demean_kontribusi_gva = df_merge$kontribusi_gva - mean(df_merge$kontribusi_gva)
df_merge$demean_treatment = df_merge$treatment - mean(df_merge$treatment)
df_merge$demean_total_pekerja = df_merge$total_pekerja - mean(df_merge$total_pekerja)
df_merge$demean_total_upah = df_merge$total_upah - mean(df_merge$total_upah)
df_merge$demean_tenaga_listrik = df_merge$tenaga_listrik - mean(df_merge$tenaga_listrik)
df_merge$demean_nilai_produksi = df_merge$nilai_produksi - mean(df_merge$nilai_produksi)
df_merge$demean_total_energi = df_merge$total_energi - mean(df_merge$total_energi)

# Creating weight based on weightit library
formula_treatment = treatment ~ kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama
formula_treatment_demean = demean_treatment ~ demean_total_pekerja + demean_total_upah + demean_tenaga_listrik + demean_nilai_produksi + demean_total_energi

W = weightit(formula_treatment, data=df_merge,
             method = 'ebal', estimand = 'ATE')

bal.tab(W, un=TRUE)
summary(W)
bobot = W$weights

W_demean = weightit(formula_treatment_demean, data=df_merge,
                   method = 'ebal', estimand = 'ATE')

bal.tab(W_demean, un=TRUE)
summary(W_demean)
bobot_demean = W_demean$weights


# Continuos treatment : weighted regression with clustered standard errors
model1 = log_gva ~ treatment
model2 = kontribusi_gva ~ treatment
model1_ext = log_gva ~ treatment + kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama
model2_ext = kontribusi_gva ~ treatment + kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama
model3_ext = demean_ln_gva ~ 0 + demean_treatment + demean_total_pekerja + demean_total_upah + demean_tenaga_listrik + demean_nilai_produksi + demean_total_energi
model4_ext = demean_kontribusi_gva ~ 0 + demean_treatment + demean_total_pekerja + demean_total_upah + demean_tenaga_listrik + demean_nilai_produksi + demean_total_energi

wls_model1 = lm(model1_ext, data = df_merge, weights = bobot)
cluster_wls_model1 = coeftest(wls_model1, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model1

wls_model2 = lm(model2_ext, data = df_merge, weights = bobot)
cluster_wls_model2 = coeftest(wls_model2, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model2

wls_model3 = lm(model3_ext, data = df_merge, weights = bobot_demean)
cluster_wls_model3 = coeftest(wls_model3, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model3

wls_model4 = lm(model4_ext, data = df_merge, weights = bobot_demean)
cluster_wls_model4 = coeftest(wls_model4, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model4


stargazer(cluster_wls_model1, cluster_wls_model2, title="Hasil Regresi",
          dep.var.labels=c('ln GVA   Kontribusi GVA'),
          out='Data Export/Hasil Regresi Tabel 1.html')

stargazer(cluster_wls_model3, cluster_wls_model4, title="Hasil Regresi Demeaning dengan Continuous Treatment",
          dep.var.labels=c('ln GVA   Kontribusi GVA'),
          out='Data Export/Hasil Regresi Tabel 3.html')


# Binary treatment: matching and weighted regression
df_merge$treatment_binary = ifelse(df_merge$treatment>0,1,0)
test_treatment_binary = treatment_binary ~ kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama

m.out = matchit(test_treatment_binary,
                data = df_merge, method = 'full', ratio = 1, distance = 'glm')
summary_text = summary(m.out)
list_excel = list(before_matching = data.frame(summary_text$sum.all, 
                                               row_names = rownames(summary_text$sum.all)),
                  after_matching = data.frame(summary_text$sum.matched,
                                              row_names = rownames(summary_text$sum.matched)),
                  matching_summary = data.frame(summary_text$nn,
                                                row_names = rownames(summary_text$nn)))

# Filename to export as an excel file
words = c('Data Export/Summary Statistic Matching Binary Treatment ', '.xlsx')
file_name_export = paste(words, collapse = "")

write_xlsx(list_excel,
           file_name_export)

# Regression with weight
match_data = match.data(m.out)
model1_binary = log_gva ~ treatment_binary + kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama
model2_binary = kontribusi_gva ~ treatment_binary + kode_klasifikasi + total_pekerja + total_upah + tenaga_listrik + nilai_produksi + total_energi + modal_utama + penjualan_utama
model3_binary = demean_ln_gva ~ 0 + treatment_binary + demean_total_pekerja + demean_total_upah + demean_tenaga_listrik + demean_nilai_produksi + demean_total_energi
model4_binary = demean_kontribusi_gva ~ 0 + treatment_binary + demean_total_pekerja + demean_total_upah + demean_tenaga_listrik + demean_nilai_produksi + demean_total_energi

wls_model1_binary = lm(model1_binary, data = match_data, weights = match_data$weights)
cluster_wls_model1_binary = coeftest(wls_model1_binary, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model1_binary

wls_model2_binary = lm(model2_binary, data = match_data, weights = match_data$weights)
cluster_wls_model2_binary = coeftest(wls_model2_binary, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model2_binary

wls_model3_binary = lm(model3_binary, data = match_data, weights = match_data$weights)
cluster_wls_model3_binary = coeftest(wls_model3_binary, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model3_binary

wls_model4_binary = lm(model4_binary, data = match_data, weights = match_data$weights)
cluster_wls_model4_binary = coeftest(wls_model4_binary, vcov=vcovCL, cluster = ~kode_klasifikasi)
cluster_wls_model4_binary


stargazer(cluster_wls_model1_binary, cluster_wls_model2_binary, title="Hasil Regresi Binary Treatment",
          dep.var.labels=c('ln GVA   Kontribusi GVA'),
          out='Data Export/Hasil Regresi Tabel 2.html')

stargazer(cluster_wls_model3_binary, cluster_wls_model4_binary, title="Hasil Regresi Demeaning dengan Binary Treatment",
          dep.var.labels=c('ln GVA   Kontribusi GVA'),
          out='Data Export/Hasil Regresi Tabel 4.html')




