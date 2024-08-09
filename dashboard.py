import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency

sns.set(style='dark')

# Fungsi untuk membuat dataframe jumlah pesanan dan revenuenya per hari
def create_daily_orders_df(df):
    delivered_orders_df = df[df['order_status'] == 'delivered']
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        'order_purchase_timestamp': 'order_date',
        'order_id': 'order_count',
        'payment_value': 'revenue'
    }, inplace=True)
    
    return daily_orders_df

# Fungsi untuk membuat dataframe jumlah pesanan per produk
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby(by='product_category_name_english').order_id.nunique().sort_values(ascending=False).reset_index()
    sum_order_items_df.rename(columns={
        'product_category_name_english': 'product_category',
        'order_id': 'order_count',
    }, inplace=True)
    
    return sum_order_items_df

# Fungsi untuk membuat dataframe jumlah pelanggan berdasarkan kota
def create_bycity_df(df):
    bygender_df = df.groupby(by='customer_city').customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)
    
    return bygender_df

# Fungsi untuk membuat dataframe jumlah pelanggan berdasarkan state
def create_bystate_df(df):
    byage_df = df.groupby(by='customer_state').customer_id.nunique().reset_index()
    byage_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)
    
    return byage_df

# Fungsi untuk membuat dataframe jumlah order berdasarkan city
def create_orders_bycity_df(df):
    orders_bycity_df = df.groupby(by='customer_city').order_id.nunique().reset_index()
    orders_bycity_df.rename(columns={
        'order_id': 'order_count'
    }, inplace=True)
    
    return orders_bycity_df

# Fungsi untuk membuat dataframe jumlah order berdasarkan state
def create_orders_bystate_df(df):
    orders_bystate_df = df.groupby(by='customer_state').order_id.nunique().reset_index()
    orders_bystate_df.rename(columns={
        'order_id': 'order_count'
    }, inplace=True)
    
    return orders_bystate_df


# Load dataset
file_path = os.path.join(os.getcwd(), 'Clean Data\\all_ecommerce_df.csv')
all_df = pd.read_csv(file_path)

# Mengubah tipe data object ke datetime
datetime_columns = ['order_purchase_timestamp']
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    

# Membuat komponen filter
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image('e-commerce-logo.png')
    
    # Mengambil start date dan end date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter data berdasarkan rentang waktu yang valid
    main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) & (all_df['order_purchase_timestamp'] <= str(end_date))]

    daily_orders_df = create_daily_orders_df(main_df)
    sum_order_items_df = create_sum_order_items_df(main_df)
    bycity_df = create_bycity_df(main_df)
    bystate_df = create_bystate_df(main_df)
    orders_bycity_df = create_orders_bycity_df(main_df)
    orders_bystate_df = create_orders_bystate_df(main_df)
    
    
# Melengkapi dashboard dengan berbagai visualisasi

# Menambahkan header
st.header('E-Commerce Public Dashboard :sparkles:')

# Menambahkan informasi daily orders
st.subheader('Penjualan Harian')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric('Total orders', value=total_orders)
    
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), 'R$', locale='es_CO')
    st.metric('Total Revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df['order_date'],
    daily_orders_df['order_count'],
    marker='o',
    linewidth=2,
    color='#90CAF9'
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# Menampilkan informasi performa penjualan dari setiap produk
st.subheader('Produk Paling Laris dan Paling Sedikit Dipesan')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ['#90CAF9', '#D3D3D3', '#D3D3D3', '#D3D3D3', '#D3D3D3']

sns.barplot(x='order_count', y='product_category', data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('Number of Sales', fontsize=30)
ax[0].set_title('Produk Paling Laris', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='order_count', y='product_category', data=sum_order_items_df.sort_values(by='order_count', ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Number of Sales', fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('Produk Paling Sedikit Dipesan', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Menampilkan demografi pelanggan
st.subheader('Demografi Pelanggan')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    sns.barplot(
        y='customer_count',
        x='customer_city',
        data=bycity_df.sort_values(by='customer_count', ascending=False).head(),
        palette=colors,
        ax=ax
    )
    
    ax.set_title('Jumlah Pelanggan Berdasarkan City', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ['#90CAF9', '#D3D3D3', '#D3D3D3', '#D3D3D3', '#D3D3D3']
    
    sns.barplot(
        y='customer_count',
        x='customer_state',
        data=bystate_df.sort_values(by='customer_count', ascending=False).head(),
        palette=colors,
        ax=ax
    )
    
    ax.set_title('Jumlah Pelanggan Berdasarkan State', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)


# Menampilkan jumlah pesanan berdasarkan lokasi geografis
st.subheader('Jumlah Pesanan Berdasarkan Lokasi Geografis')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    sns.barplot(
        y='order_count',
        x='customer_city',
        data=orders_bycity_df.sort_values(by='order_count', ascending=False).head(),
        palette=colors,
        ax=ax
    )
    
    ax.set_title('Jumlah Pesanan Berdasarkan City', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ['#90CAF9', '#D3D3D3', '#D3D3D3', '#D3D3D3', '#D3D3D3']
    
    sns.barplot(
        y='order_count',
        x='customer_state',
        data=orders_bystate_df.sort_values(by='order_count', ascending=False).head(),
        palette=colors,
        ax=ax
    )
    
    ax.set_title('Jumlah Pesanan Berdasarkan State', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.caption('Copyright (c) E-Commerce-Public 2024')