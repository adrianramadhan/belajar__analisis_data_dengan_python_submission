import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Helper Function
def count_by_day_df(day_df):
    day_df_count = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def rental_by_day_type(day_df):
    rental_day = day_df.groupby('category_days')['count_cr'].sum().reset_index()
    return rental_day

def rental_by_hour_type(hour_df):
    hour_df['work_hours'] = hour_df['hours'].apply(lambda x: 'Work Hours' if 9 <= x <= 17 else 'Non-Work Hours')
    rental_by_work_hours = hour_df.groupby('work_hours')['count_cr'].sum().reset_index()
    return rental_by_work_hours

def rental_peak_time(hour_df):
    return hour_df.groupby('hours')['count_cr'].sum().reset_index()

def total_rental_by_hours_and_days(hour_df):
    hour_df['category_days'] = hour_df['one_of_week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
    total_user_hour_day = hour_df.groupby(['hours', 'category_days']).count_cr.sum().unstack()
    return total_user_hour_day

def create_rfm_df(hour_df):
    last_date = hour_df['dteday'].max()
    rfm_df = hour_df.groupby('registered').agg({
        'dteday': lambda x: (last_date - x.max()).days,  # Recency
        'count_cr': 'count',
        'casual': 'sum'
    }).reset_index()

    rfm_df.columns = ['user_id', 'Recency', 'Frequency', 'Monetary']

    return rfm_df


days_df = pd.read_csv("day_clean.csv")
hours_df = pd.read_csv("hour_clean.csv")

datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://cdni.iconscout.com/illustration/premium/thumb/man-buying-bike-on-rent-from-rental-agent-illustration-download-in-svg-png-gif-file-formats--renting-service-pack-vehicle-illustrations-4825725.png?f=webp")
    
        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
  
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

day_df_count = count_by_day_df(main_df_days)
registered_df = total_registered_df(main_df_days)
casual_df = total_casual_df(main_df_days)
day_type_df = rental_by_day_type(main_df_days)
hour_type_df = rental_by_hour_type(main_df_hour)
rental_peak_df = rental_peak_time(main_df_hour)
rental_by_day_hour_df = total_rental_by_hours_and_days(main_df_hour)
rfm_df = create_rfm_df(main_df_hour)

# Visualisasi Data pada Dashboard
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Peminjaman Harian')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count.count_cr.sum()
    st.metric("Total Peminjaman Sepeda", value=total_orders)

with col2:
    total_sum = registered_df.register_sum.sum()
    st.metric("Total Pengguna Terdaftar", value=total_sum)

with col3:
    total_sum = casual_df.casual_sum.sum()
    st.metric("Total Pengguna Casual", value=total_sum)

st.subheader('Jumlah Penyewaan Sepeda Berdasarkan Hari kerja dan Libur')

# Membuat visualisasi bar plot untuk Visualisasi Peminjaman berdasarkan Tipe Hari
plt.figure(figsize=(8, 5))
sns.barplot(x='category_days', y='count_cr', data=day_type_df, palette='viridis')
plt.xlabel('Tipe Hari')
plt.ylabel('Jumlah Penyewaan')
plt.xticks(rotation=45)
st.pyplot(plt)

# Menghitung perbedaan
weekday_rentals = day_type_df[day_type_df['category_days'] == 'weekdays']['count_cr'].values[0]
weekend_rentals = day_type_df[day_type_df['category_days'] == 'weekend']['count_cr'].values[0]
difference = weekday_rentals - weekend_rentals

# Menampilkan hasil perhitungan
st.write(f'Jumlah penyewaan pada hari kerja: {weekday_rentals}')
st.write(f'Jumlah penyewaan pada hari libur: {weekend_rentals}')
st.write(f'Perbedaan jumlah penyewaan: {difference}')

st.subheader('Jumlah Penyewaan Sepeda Berdasarkan Jam Kerja dan Non Kerja')

# Membuat visualisasi bar plot untuk Visualisasi Peminjaman berdasarkan Jam Kerja dan Non
plt.figure(figsize=(8, 5))
sns.barplot(x='work_hours', y='count_cr', data=hour_type_df, palette='coolwarm')
plt.xlabel('Jam Kerja')
plt.ylabel('Jumlah Penyewaan')
plt.xticks(rotation=45)
st.pyplot(plt)

# Menghitung Selisih
work_hours_rentals = hour_type_df[hour_type_df['work_hours'] == 'Work Hours']['count_cr'].values[0]
non_work_hours_rentals = hour_type_df[hour_type_df['work_hours'] == 'Non-Work Hours']['count_cr'].values[0]
difference_work_hours = work_hours_rentals - non_work_hours_rentals

# Menampilkan hasil perhitungan
st.write(f'Jumlah penyewaan pada jam kerja: {work_hours_rentals}')
st.write(f'Jumlah penyewaan pada jam non-kerja: {non_work_hours_rentals}')
st.write(f'Perbedaan jumlah penyewaan: {difference_work_hours}')

st.subheader('Tren Penyewaan Sepeda Per Jam')

# Visualisasi jumlah penyewaan per jam
plt.figure(figsize=(12, 6))
sns.lineplot(data=rental_peak_df, x='hours', y='count_cr', marker='o')
plt.title('Jumlah Penyewaan Sepeda per Jam')
plt.xlabel('Jam dalam Sehari')
plt.ylabel('Jumlah Penyewaan')
plt.xticks(range(0, 24))  # Menampilkan jam dari 0 hingga 23
plt.grid()
st.pyplot(plt)

st.subheader('Perbandingan Jumlah Penyewaan Sepeda Antara Pengguna Terdaftar Dan Kasual')

# Visualisasi Pie Chart
labels = ['Registered', 'Casual']
sizes = [main_df_days['registered'].sum(), main_df_days['casual'].sum()]
colors = ['#1f77b4', '#ff7f0e']
explode = (0.1, 0) 

plt.figure(figsize=(8, 6))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.axis('equal')
plt.title('Perbandingan Penyewaan Sepeda: Registered vs Casual')
st.pyplot(plt)

st.subheader('Tren Penyewaan Sepeda Berdasarkan Jam dan Kategori Hari')

# Visualisasi
plt.figure(figsize=(12, 6))
rental_by_day_hour_df.plot(kind='bar')
plt.xlabel('Jam dalam Sehari')
plt.ylabel('Total Penyewaan')
plt.xticks(rotation=0)
plt.legend(title='Kategori Hari')
st.pyplot(plt)

# Menampilkan analisis RFM
st.subheader('Analisis RFM untuk Penyewaan Sepeda')
st.write("""
**Analisis RFM** (Recency, Frequency, Monetary) adalah teknik yang digunakan untuk mengidentifikasi dan mengelompokkanpelanggan berdasarkan perilaku mereka. 
- **Recency**: Mengukur seberapa baru pelanggan melakukan transaksi. Semakin kecil nilainya, semakin baru transaksi terakhir.
- **Frequency**: Mengukur seberapa sering pelanggan melakukan transaksi dalam periode waktu tertentu.
- **Monetary**: Mengukur total nilai transaksi yang dilakukan oleh pelanggan.
Analisis ini membantu dalam memahami perilaku pelanggan dan dapat digunakan untuk strategi pemasaran yang lebih efektif.
""")
# Menampilkan DataFrame RFM
st.dataframe(rfm_df)