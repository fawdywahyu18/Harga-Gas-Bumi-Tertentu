"""
Membuat jembatan panel antara tahun 2014 ke tahun 2015
untuk menjawab dampak penerapan harga gas bumi tertentu pada tahun 2016
melalui perpres nomor 40 tahun 2016

@author: fawdywahyu
"""

import pandas as pd

ibs_2015 = pd.read_stata('Data/ibs_2015.dta', 
                         convert_categoricals=True,
                         convert_missing=False, 
                         preserve_dtypes=True)

ibs_2017 = pd.read_stata('Data/ibs_2017.dta', 
                         convert_categoricals=True,
                         convert_missing=False, 
                         preserve_dtypes=True)


# Cek apakah renum dari kedua tahun merupakan perusahaan yang sama atau tidak
# Cara ngeceknya pakai ibs tahun 2013 dan 2014, dicek menggunakan kode prov, kode kab/kota, dan KBLI 5 digit.
colnames_2015 = ibs_2015.columns
colnames_2017 = ibs_2017.columns

renum_2015 = ibs_2015['RENUM']
renum_2017 = ibs_2017['RENUM']

ibs_2015_slice = ibs_2015[['RENUM', 'DISIC215']]
ibs_2017_slice = ibs_2017[['RENUM', 'DISIC517']]
ibs_2015_slice['DISIC215'] = pd.to_numeric(ibs_2015_slice['DISIC215'])
ibs_2017_slice['DISIC517'] = pd.to_numeric(ibs_2017_slice['DISIC517'])

df_merge = pd.merge(left=ibs_2015_slice, right=ibs_2017_slice,
                    on='RENUM', how='inner')

df_merge['Check apakah KBLI konsisten'] = df_merge['DISIC215'] == df_merge['DISIC517']
freq_table_check = df_merge['Check apakah KBLI konsisten'].value_counts(normalize=True)
# terbukti bahwa proporsi "True" sekitar 93%, artinya renum bisa digunakan untuk merge

# Fuzzy Matching IBS 2014 dan 2015
ibs_2014 = pd.read_csv('Data/ibs_2014.csv',
                        low_memory=False)
ibs_2014.rename(columns=lambda x: x.lower(), inplace=True)
colnames_2014 = ibs_2014.columns

ibs_2015.rename(columns=lambda x: x.lower(), inplace=True)


# Variabel yang bisa digunakan untuk membangun id
# 1. Status penanaman modal
# 2. Total Pekerja
# 3. KBLI 2 Digit

# Status penanaman modal bisa menggunakan:
# 1. dpusat14, dpemda14, dst kemudian diidentifikasi mana persentase penanaman modal terbesar
# 2. dstat14

def creating_id(ibs_input_before):
    
    # ibs_input = ibs_2014

    colnames = ibs_input_before.columns
    kolom_tahun = colnames[10]
    dua_digit_tahun = kolom_tahun[-2:]
    
    # Drop observasi yang berisi nan untuk gas bumi
    ibs_input_before['Penggunaan Gas Bumi'] = ibs_input_before[f'egavcu{dua_digit_tahun}'] + ibs_input_before[f'egovcu{dua_digit_tahun}'] 
    ibs_input = ibs_input_before.dropna(subset=['Penggunaan Gas Bumi'])
    
    # Persentase Permodalan
    modal_pempus = ibs_input[(f'dpusat{dua_digit_tahun}')]
    modal_pemda = ibs_input[(f'dpemda{dua_digit_tahun}')]
    modal_swasta_nasional = ibs_input[(f'ddmstk{dua_digit_tahun}')]
    modal_asing = ibs_input[(f'dasing{dua_digit_tahun}')]
    
    # KBLI 2 Digit
    if dua_digit_tahun=='14':
        kbli = ibs_input[f'disic5{dua_digit_tahun}'].astype(str)
        kbli = kbli.str[:2]
        identifikasi = ibs_input['psid'].astype(str)
    else:
        kbli = ibs_input[f'disic2{dua_digit_tahun}'].astype(str)
        identifikasi = ibs_input['renum'].astype(str)
    
    # Pembagian kategori pekerja berdasarkan persentil
    kelompok_pekerja = pd.qcut(ibs_input[f'ltlnou{dua_digit_tahun}'], 10, labels=False)
    total_pekerja = ibs_input[f'ltlnou{dua_digit_tahun}']
    
    # Pembagian nilai total barang berdasarkan persentil
    kelompok_nilai_barang = pd.qcut(ibs_input[f'yprvcu{dua_digit_tahun}'], 10, labels=False)
    
    # Pembagian nilai bahan bakar dan pelumas berdasarkan persentil
    kelompok_nilai_bb = pd.qcut(ibs_input[f'efuvcu{dua_digit_tahun}'], 10, labels=False)
    
        
    ibs_slice_dict = {
        'modal pempus': modal_pempus,
        'modal pemda': modal_pemda,
        'modal swasta': modal_swasta_nasional,
        'modal asing': modal_asing,
        'kbli 2 digit': kbli,
        'kategori pekerja': kelompok_pekerja,
        'total pekerja': total_pekerja,
        f'ID{dua_digit_tahun}':identifikasi,
        'kelompok nilai barang': kelompok_nilai_barang,
        'kelompok nilai bahan bakar': kelompok_nilai_bb}
    
    ibs_slice = pd.DataFrame(ibs_slice_dict)
    
    ibs_slice['Sumber Modal Utama'] = ibs_slice[['modal pempus', 'modal pemda',
                                                 'modal swasta', 'modal asing']].idxmax(axis=1)
    ibs_slice['kategori pekerja str'] = ibs_slice['kategori pekerja'].astype(str)
    ibs_slice['kategori nilai barang str'] = ibs_slice['kelompok nilai barang'].astype(str)
    ibs_slice['kategori nilai bahan bakar'] = ibs_slice['kelompok nilai bahan bakar'].astype(str)
    ibs_slice['total pekerja str'] = ibs_slice['total pekerja'].astype(str)
    
    ibs_slice[f'ID fuzzy match {dua_digit_tahun}'] = ibs_slice['Sumber Modal Utama'] + ' ' + ibs_slice['kbli 2 digit'] + ' ' + ibs_slice['kategori pekerja str'] + ' ' + ibs_slice['kategori nilai barang str'] + ' ' + ibs_slice['kategori nilai bahan bakar'] + ' ' + ibs_slice['total pekerja str']
    
    ibs_result = ibs_slice[[f'ID fuzzy match {dua_digit_tahun}', f'ID{dua_digit_tahun}']]
    ibs_result = ibs_result.drop_duplicates(subset=[f'ID fuzzy match {dua_digit_tahun}'])
    # len(ibs_result[f'ID fuzzy match {dua_digit_tahun}'].unique()) == ibs_result.shape[0]
    
    return ibs_result

ibs_2014_fuzzy = creating_id(ibs_2014)
ibs_2015_fuzzy = creating_id(ibs_2015)

len(ibs_2014_fuzzy['ID fuzzy match 14'].unique()) == ibs_2014_fuzzy.shape[0] # cek apakah id yg dibuat sudah unik atau belum, harus unik/True
len(ibs_2015_fuzzy['ID fuzzy match 15'].unique()) == ibs_2015_fuzzy.shape[0]


from thefuzz import fuzz
from thefuzz import process

# Check the similarity score
full_name = "Kurtis K D Pykes"
full_name_reordered = "Kurtis Pykes K D"

# Order does not matter for token sort ratio
# print(f"Token sort ratio similarity score: {fuzz.token_sort_ratio(full_name_reordered, full_name)}")# Order matters for partial ratio
# print(f"Partial ratio similarity score: {fuzz.partial_ratio(full_name, full_name_reordered)}")
# Order will not effect simple ratio if strings do not match
# print(f"Simple ratio similarity score: {fuzz.ratio(name, full_name)}")

id_2014 = ibs_2014_fuzzy['ID fuzzy match 14'].iloc[0]
id_2015 = ibs_2015_fuzzy['ID fuzzy match 15'].iloc[0]
fuzz.ratio(id_2014, id_2015)

# Rename the misspelled columns
ibs_2014_fuzzy['ID fuzzy match 14 after correction'] = ibs_2014_fuzzy['ID fuzzy match 14'].apply(
  lambda x: process.extractOne(x,ibs_2015_fuzzy['ID fuzzy match 15'], scorer=fuzz.partial_ratio)[0]
)

ibs_2014_fuzzy_unique = ibs_2014_fuzzy.drop_duplicates(subset=['ID fuzzy match 14 after correction'])

# Merge after fuzzy correction
ibs_merge = pd.merge(left=ibs_2014_fuzzy_unique, right=ibs_2015_fuzzy,
                     left_on='ID fuzzy match 14 after correction',
                     right_on='ID fuzzy match 15',
                     how='inner')
len(ibs_merge['ID15'].unique()) == ibs_merge.shape[0]

# Merge untuk mendapatkan KBLI 5 digit, kode kabupaten kota, dan kode provinsi
ibs_2014_kode = ibs_2014[['psid', 'dprovi14', 'dkabup14', 'disic514']]
ibs_2014_kode.columns = ['ID14', 'Kode Provinsi', 'Kode Kabupaten', 'KBLI 5 Digit']
ibs_2014_kode['ID14 str'] = ibs_2014_kode['ID14'].astype(str)
ibs_merge_kode_lengkap = pd.merge(left=ibs_merge, right=ibs_2014_kode[['ID14 str', 'Kode Provinsi', 'Kode Kabupaten', 'KBLI 5 Digit']],
                                  right_on='ID14 str', left_on='ID14',
                                  how='inner')
ibs_merge_kode_lengkap.to_excel('Data/Kode Lengkap 2014 dan 2015.xlsx', index=False)
    
    
 
