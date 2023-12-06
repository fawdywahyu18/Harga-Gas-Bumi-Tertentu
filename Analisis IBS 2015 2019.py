"""
Mengidentifikasi Industri apa yang paling tepat sebagai sasaran kebijakan 
subsidi harga gas bumi (HGBT)
Membuat data panel IBS dari tahun 2015 ke 2019

@author: fawdywahyu
"""

import pandas as pd
import numpy as np

def analisis_dasar(tahun):
    
    # analisis dasar memuat cleaning dan creating new variables
    
    # tahun: str
    # tahun = '2015'
    
    # Import Data
    ibs_dta = pd.read_stata(f'Data/ibs_{tahun}.dta', 
                            convert_categoricals=True,
                            convert_missing=False, 
                            preserve_dtypes=True)

    # Import data deflator
    deflator = pd.read_excel('Data/Deflator Indonesia.xlsx', sheet_name='Deflator Indonesia')
    deflator.set_index('Year', inplace=True)
    
    # Karakteristik Perusahaan
    ibs_copy = ibs_dta.copy()
    ibs_copy.rename(columns=lambda x: x.lower(), inplace=True)
    dua_digit_tahun = tahun[-2:]
    
    # Persentase Permodalan
    modal_pempus = ibs_copy[(f'dpusat{dua_digit_tahun}')]
    modal_pemda = ibs_copy[(f'dpemda{dua_digit_tahun}')]
    modal_swasta_nasional = ibs_copy[(f'ddmstk{dua_digit_tahun}')]
    modal_asing = ibs_copy[(f'dasing{dua_digit_tahun}')]
    
    # Jumlah pekerja
    jumlah_pekerja = ibs_copy[(f'ltlnou{dua_digit_tahun}')]
    
    # Upah
    ibs_copy['total upah'] = ibs_copy[(f'zndvcu{dua_digit_tahun}')] + ibs_copy[(f'zpdvcu{dua_digit_tahun}')]
    wage = ibs_copy['total upah']
    
    # Kekuatan Tenaga Listrik
    tenaga_listrik = ibs_copy[(f'esgkhu{dua_digit_tahun}')]
    
    # Persentase tujuan penjualan
    # penjualan_intra = ibs_copy[(f'pryrsg{dua_digit_tahun}')]
    # penjualan_perusahaan_lain = ibs_copy[(f'pryrom{dua_digit_tahun}')]
    # penjualan_pedagang_besar = ibs_copy[(f'pryrwh{dua_digit_tahun}')]
    # penjualan_eceran = ibs_copy[(f'pryrre{dua_digit_tahun}')]
    # penjualan_pemerintah = ibs_copy[(f'pryrin{dua_digit_tahun}')]
    
    # Nilai produksi
    nilai_produksi = ibs_copy[(f'yprvcu{dua_digit_tahun}')]
    
    # persentase maklun
    maklun_dalam_negeri = ibs_copy[(f'yisvdo{dua_digit_tahun}')]
    maklun_luar_negeri = ibs_copy[(f'yisvfo{dua_digit_tahun}')]
    total_maklun = ibs_copy[(f'yisvcu{dua_digit_tahun}')]
    persentase_maklun_dn = maklun_dalam_negeri/total_maklun
    persentase_maklun_ln = maklun_luar_negeri/total_maklun
    
    
    # Treatment Variable
    # Treatment adalah persentase utilisasi gas bumi terhadap total energi yang
    # digunakan oleh perusahaan dalam satu tahun
    # Pakai nilai aja, bukan volume karena ingin melihat industri mana yg cocok
    # menerima subsidi. Subsidi selalu terkait dengan harga dan nilai, bukan subsidi volume.
    # Treatment berupa persentase untuk mengakomodir pertanyaan, apabila ada perpindahan
    # penggunaan bahan bakar dari jenis bahan bakar lain ke gas bumi, efeknya gimana
    # treatment dapat berupa volume gas bumi dan nilai gas bumi.
    
    gas_pgn = ibs_copy[(f'egavcu{dua_digit_tahun}')]
    gas_non_pgn = ibs_copy[(f'egovcu{dua_digit_tahun}')]
    nilai_gas = gas_pgn + gas_non_pgn
    nilai_bensin = ibs_copy[(f'epevcu{dua_digit_tahun}')]
    nilai_solar = ibs_copy[(f'esovcu{dua_digit_tahun}')]
    nilai_batubara = ibs_copy[(f'eclvcu{dua_digit_tahun}')]
    nilai_briket = ibs_copy[(f'ecbvcu{dua_digit_tahun}')]
    nilai_lpg = ibs_copy[(f'elpvcu{dua_digit_tahun}')]
    nilai_pelumas = ibs_copy[(f'eluvcu{dua_digit_tahun}')]
    
    total_bahan_bakar = ibs_copy[(f'efuvcu{dua_digit_tahun}')]
    persentase_gas = nilai_gas / total_bahan_bakar
    persentase_bensin = nilai_bensin / total_bahan_bakar
    persentase_solar = nilai_solar / total_bahan_bakar
    persentase_batubara = nilai_batubara / total_bahan_bakar
    persentase_briket = nilai_briket / total_bahan_bakar
    persentase_lpg = nilai_lpg / total_bahan_bakar
    persentase_pelumas = nilai_pelumas / total_bahan_bakar
    persentase_lainnya = 1 - (persentase_gas+persentase_bensin+persentase_solar+persentase_batubara+persentase_briket+persentase_lpg+persentase_pelumas)
    
    
    # Berdasarkan volume
    vol_gas_pgn = ibs_copy[(f'egam3u{dua_digit_tahun}')]
    vol_gas_non_pgn = ibs_copy[(f'egom3u{dua_digit_tahun}')]
    vol_bensin = ibs_copy[(f'epeliu{dua_digit_tahun}')]
    vol_solar = ibs_copy[(f'esoliu{dua_digit_tahun}')]
    vol_batubara = ibs_copy[(f'eclkgu{dua_digit_tahun}')]
    vol_briket = ibs_copy[(f'ecbkgu{dua_digit_tahun}')]
    vol_lpg = ibs_copy[(f'elpkgu{dua_digit_tahun}')]
    vol_pelumas = ibs_copy[(f'eluliu{dua_digit_tahun}')]
    vol_bahan_bakar = vol_gas_pgn + vol_gas_non_pgn + vol_bensin + vol_solar + vol_batubara + vol_briket + vol_lpg + vol_pelumas
    vol_persentase_gas = (vol_gas_pgn + vol_gas_non_pgn)/vol_bahan_bakar
    vol_persentase_bensin = vol_bensin/vol_bahan_bakar
    vol_persentase_solar = vol_solar/vol_bahan_bakar
    vol_persentase_batubara = vol_batubara/vol_bahan_bakar
    vol_persentase_briket = vol_briket/vol_bahan_bakar
    vol_persentase_lpg = vol_lpg/vol_bahan_bakar
    vol_persentase_pelumas = vol_pelumas/vol_bahan_bakar
    
    # Kode Klasifikasi Industri
    if tahun=='2015':
        klasifikasi = ibs_copy['disic215']
    elif tahun=='2017':
        klasifikasi = ibs_copy['disic517']
    elif tahun=='2018':
        klasifikasi = ibs_copy['disic518']
    elif tahun=='2019':
        klasifikasi = ibs_copy['disic519']
    
    renum = ibs_copy['renum']
    
    # Intermediate good cost
    intermediate_cost = ibs_copy[f'iinput{dua_digit_tahun}']
    
    
    # Outcome variable
    
    # Nilai Tambah (Gross Value Add) dan Profit
    nominal_gva = ibs_copy[(f'vtlvcu{dua_digit_tahun}')]
    # inflasi_deflator = deflator.loc[tahun, 'Deflator Percentage'].values[0]
    deflator_pdb = deflator.loc[tahun, 'Deflator Index 2010_1'].values[0]
    # pengali = 1 + inflasi_deflator/100
    real_gva = nominal_gva / deflator_pdb
    nominal_profit = nominal_gva - wage
    
    # Total Pendapatan
    total_pendapatan = ibs_copy[(f'output{dua_digit_tahun}')]
    pajak_perusahaan = ibs_copy[(f'itxvcu{dua_digit_tahun}')]
    
    tahun_series = pd.Series(tahun, index=range(ibs_copy.shape[0]))
    
    # Dijadikan satu dataframe
    result = {
        'Kode Klasifikasi': klasifikasi,
        'Renum': renum,
        'Tahun': tahun_series,
        'Modal Pempus': modal_pempus/100,
        'Modal Pemda': modal_pemda/100,
        'Modal Swasta': modal_swasta_nasional/100,
        'Modal Asing': modal_asing/100,
        'Total Pekerja': jumlah_pekerja,
        'Total Upah': wage,
        'Tenaga Listrik': tenaga_listrik,
        # 'Penjualan Intra': penjualan_intra/100,
        # 'Penjualan Perusahaan Lain': penjualan_perusahaan_lain/100,
        # 'Penjualan Pedagang Besar': penjualan_pedagang_besar/100,
        # 'Penjualan Eceran': penjualan_eceran/100,
        # 'Penjualan Pemerintah': penjualan_pemerintah/100,
        'Nilai Produksi': nilai_produksi,
        'Maklun Dalam Negeri': persentase_maklun_dn,
        'Maklun Luar Negeri': persentase_maklun_ln,
        'Total Maklun': total_maklun,
        'Nilai Gas Bumi': nilai_gas,
        'Total Nilai Bahan Bakar': total_bahan_bakar,
        'Persentase Nilai Gas Bumi': persentase_gas,
        'Persentase Nilai Bensin': persentase_bensin,
        'Persentase Nilai Solar': persentase_solar,
        'Persentase Nilai Batubara': persentase_batubara,
        'Persentase Nilai Briket': persentase_briket,
        'Persentase Nilai LPG': persentase_lpg,
        'Persentase Nilai Pelumas': persentase_pelumas,
        'Persentase Nilai Bahan Bakar Lainnya': persentase_lainnya,
        'Volume Gas Bumi': vol_gas_pgn + vol_gas_non_pgn,
        'Total Volume Bahan Bakar': vol_bahan_bakar,
        'Persentase Volume Gas Bumi': vol_persentase_gas,
        'Persentase Volume Bensin': vol_persentase_bensin,
        'Persentase Volume Solar': vol_persentase_solar,
        'Persentase Volume Batubara': vol_persentase_batubara,
        'Persentase Volume Briket': vol_persentase_briket,
        'Persentase Volume LPG': vol_persentase_lpg,
        'Persentase Volume Pelumas': vol_persentase_pelumas,
        'Nominal GVA': nominal_gva,
        'Real GVA': real_gva,
        'Nominal Profit': nominal_profit,
        'Total Pendapatan': total_pendapatan,
        'Pajak Perusahaan': pajak_perusahaan,
        'Biaya Barang Input': intermediate_cost
        }
    result_df = pd.DataFrame(result)
    return result_df

# Analisis Tabel by Industri
def analisis_industri(df_input, metode_agg='median'):
    
    # df_input : dataframe input dari hasil analisis_dasar
    # df_input = analisis_dasar_2015
    # metode_agg : str, merupakan string untuk metode agregasi
    
    df_olah = df_input.copy()
    df_grouped = df_olah.groupby('Kode Klasifikasi').agg({'Tahun': lambda x: x.iloc[0],
                                                          'Modal Pempus': metode_agg,
                                                          'Modal Pemda': metode_agg,
                                                          'Modal Swasta': metode_agg,
                                                          'Modal Asing': metode_agg,
                                                          'Total Pekerja': metode_agg,
                                                          'Total Upah': metode_agg,
                                                          'Tenaga Listrik': metode_agg,
                                                          # 'Penjualan Intra': metode_agg,
                                                          # 'Penjualan Perusahaan Lain': metode_agg,
                                                          # 'Penjualan Pedagang Besar': metode_agg,
                                                          # 'Penjualan Eceran': metode_agg,
                                                          # 'Penjualan Pemerintah': metode_agg,
                                                          'Nilai Produksi': metode_agg,
                                                          'Maklun Dalam Negeri': metode_agg,
                                                          'Maklun Luar Negeri': metode_agg,
                                                          'Total Maklun': metode_agg,
                                                          'Nilai Gas Bumi': metode_agg,
                                                          'Total Nilai Bahan Bakar': metode_agg,
                                                          'Persentase Nilai Gas Bumi': metode_agg,
                                                          'Persentase Nilai Bensin': metode_agg,
                                                          'Persentase Nilai Solar': metode_agg,
                                                          'Persentase Nilai Batubara': metode_agg,
                                                          'Persentase Nilai Briket': metode_agg,
                                                          'Persentase Nilai LPG': metode_agg,
                                                          'Persentase Nilai Pelumas': metode_agg,
                                                          'Persentase Nilai Bahan Bakar Lainnya': metode_agg,
                                                          'Volume Gas Bumi': metode_agg,
                                                          'Total Volume Bahan Bakar': metode_agg,
                                                          'Persentase Volume Gas Bumi': metode_agg,
                                                          'Persentase Volume Bensin': metode_agg,
                                                          'Persentase Volume Solar': metode_agg,
                                                          'Persentase Volume Batubara': metode_agg,
                                                          'Persentase Volume Briket': metode_agg,
                                                          'Persentase Volume LPG': metode_agg,
                                                          'Persentase Volume Pelumas': metode_agg,
                                                          'Nominal GVA':metode_agg,
                                                          'Real GVA':metode_agg,
                                                          'Nominal Profit':metode_agg,
                                                          'Total Pendapatan': metode_agg,
                                                          'Pajak Perusahaan': metode_agg,
                                                          'Biaya Barang Input': metode_agg}).reset_index()

    return df_grouped

def klasifikasi_kolum(df_tahun):
    # Melakukan identifikasi sumber modal utama dan tujuan penjualan utama
    
    # df_tahun = df_2019.copy()
    df_tahun['Sumber Modal Utama'] = df_tahun[['Modal Pempus', 'Modal Pemda',
                                               'Modal Swasta', 'Modal Asing']].idxmax(axis=1)
    # df_tahun['Tujuan Penjualan Utama'] = df_tahun[['Penjualan Perusahaan Lain', # 'Penjualan Intra', 
                                                   # 'Penjualan Pedagang Besar', # 'Penjualan Eceran',
                                                   # 'Penjualan Pemerintah']].idxmax(axis=1)
    df_tahun['Domestik atau Ekspor'] = df_tahun[['Maklun Dalam Negeri', 'Maklun Luar Negeri']].idxmax(axis=1)
    # Kolom Domestik atau Ekspor tidka terpilih karena banyak NaN
    
    kolom_terpilih = ['Tahun', 'Kode Klasifikasi', 'Renum', 'Total Pekerja',
                      'Total Upah', 'Tenaga Listrik', 'Nilai Produksi',
                      'Nilai Gas Bumi', 'Volume Gas Bumi',
                      'Persentase Nilai Gas Bumi', 'Persentase Volume Gas Bumi',
                      'Total Volume Bahan Bakar', 'Total Maklun',
                      'Nominal GVA', 'Nominal Profit',
                      'Biaya Barang Input', 'Sumber Modal Utama'] # ,
                      # 'Tujuan Penjualan Utama']
    df_terpilih = df_tahun[kolom_terpilih]
    df_terpilih['Nilai Gas Bumi'] = df_terpilih['Nilai Gas Bumi'].replace(np.nan, 0)
    df_terpilih['Volume Gas Bumi'] = df_terpilih['Volume Gas Bumi'].replace(np.nan, 0)
    df_terpilih['Persentase Nilai Gas Bumi'] = df_terpilih['Persentase Nilai Gas Bumi'].replace(np.nan, 0)
    df_terpilih['Persentase Volume Gas Bumi'] = df_terpilih['Persentase Volume Gas Bumi'].replace(np.nan, 0)
    
    tahun = df_terpilih['Tahun'][0]
    suffix_string = f'_{tahun}'
    df_suffixed = df_terpilih.add_suffix(suffix_string)
    
    # rename a single column of renum
    df_suffixed.rename(columns={f'Renum_{tahun}': 'Renum'}, inplace=True)
    
    return df_suffixed

# 2019
df_2019 = analisis_dasar('2019')
industri_2019 = analisis_industri(df_2019)
df_2019_selected = klasifikasi_kolum(df_2019)

# 2018
df_2018 = analisis_dasar('2018')
industri_2018 = analisis_industri(df_2018)
df_2018_selected = klasifikasi_kolum(df_2018)

# 2017
df_2017 = analisis_dasar('2017')
industri_2017 = analisis_industri(df_2017)
df_2017_selected = klasifikasi_kolum(df_2017)

# 2015
df_2015 = analisis_dasar('2015')
industri_2015 = analisis_industri(df_2015)
df_2015_selected = klasifikasi_kolum(df_2015)


# Creating long format panel from 2015-2019
renum_2015 = df_2015_selected['Renum']
len(renum_2015) == len(df_2015_selected['Renum'].unique()) # Kalau hasilnya True, artinya renum bersifat unik

# Merge dataframes from 2015-2019
merged_df = pd.merge(pd.merge(pd.merge(df_2015_selected, df_2017_selected, on='Renum'), df_2018_selected, on='Renum'), df_2019_selected, on='Renum')
nk_merged = merged_df.columns

list_tahun = ['2015', '2017', '2018', '2019']

for t in list_tahun:
    df_x = merged_df.filter(regex=f'_{t}')
    df_x['Renum'] = merged_df['Renum']
    df_x.columns = df_x.columns.str.replace(f'_{t}', '')
    
    if t==list_tahun[0]:
        append_df = df_x
    else:
        append_df = pd.concat([append_df, df_x], axis=0)
