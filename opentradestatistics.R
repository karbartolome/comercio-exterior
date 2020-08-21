setwd("~/Documents/Analisis/datos_comercio/comercio-exterior")
options(scipen=999)
library(tradestatistics)
library(dplyr)

paises = ots_countries
productos = ots_products
productos_short = ots_products_shortnames
sections = ots_sections
sections_names = ots_sections_shortnames
grupos = ots_groups


df=readRDS("/Users/karinabartolome/Downloads/yrpc-2018.rds")

df = df %>% left_join(sections, by='product_code') 
df = df %>% left_join(grupos, by='product_code')

df_section_exports = df %>% 
  group_by(reporter_iso,partner_iso,section_code) %>% 
  summarise(export_value_usd=sum(export_value_usd)) %>% 
  ungroup() %>% 
  filter(!is.na(export_value_usd)) %>% 
  left_join(sections_names, by='section_code') %>% 
  left_join(paises %>% select(reporter_iso=country_iso,reporter=country_name_english), by='reporter_iso') %>% 
  left_join(paises %>% select(partner_iso=country_iso,partner=country_name_english), by='partner_iso') %>% 
  select(reporter, partner, section=section_shortname_english, export_value_usd) 

write.csv(df_section_exports, '/Users/karinabartolome/Documents/Analisis/datos_comercio/df.csv')







a=df_section_exports %>% filter(export_value_usd >= quantile(df_section_exports$export_value_usd, .25))
a = a %>% filter(section=='Chemical Products')



df_section_exports = df %>% 
  group_by(reporter_iso,partner_iso,section_code) %>% 
  summarise(export_value_usd=sum(export_value_usd)) %>% 
  ungroup() %>% 
  filter(!is.na(export_value_usd)) %>% 
  left_join(sections_names, by='section_code') %>% 
  left_join(paises %>% select(reporter_iso=country_iso,reporter=country_name_english), by='reporter_iso') %>% 
  left_join(paises %>% select(partner_iso=country_iso,partner=country_name_english), by='partner_iso') %>% 
  select(reporter, partner, section=section_shortname_english, export_value_usd)

a=df_section_exports %>% filter(export_value_usd >= quantile(df_section_exports$export_value_usd, .25))
a = a %>% filter(section=='Chemical Products')








df_section_imports = df %>% 
  group_by(reporter_iso,partner_iso,section_code) %>% 
  summarise(import_value_usd=sum(import_value_usd)) %>% 
  filter(!is.na(import_value_usd)) %>% 
  left_join(sections_names, by='section_code') %>% 
  left_join(paises %>% select(reporter_iso=country_iso,reporter=country_name_english), by='reporter_iso') %>% 
  left_join(paises %>% select(partner_iso=country_iso,partner=country_name_english), by='partner_iso')










prod = ots_product_code("Warp knit fabrics")
sect = ots_product_section("Chemical") %>% left_join(productos_short, by='product_code')

paises %>% filter(paises$continent=='Americas') %>% select(country_name_english)

sect = sections %>% filter(section_code=='01')
sect = unique(sect$product_code)
sect = productos %>% filter(product_code %in% sect)


df <- ots_create_tidy_data(
  years = 2018,
  products = '0101',
  reporters = 'all',
  table = "yrpc"
) %>% select(
  reporter_iso,
  partner_iso,
  product_code,
  product_shortname_english,
  export_value_usd,
  import_value_usd
) %>% filter(reporter_iso != partner_iso) 




df <- ots_create_tidy_data(
  years = 2018,
  #products = paste0("'",gsub(',',"','",paste(sect$product_code, collapse=',')),"'"),
  sections = '01',
  reporters = 'all',
  table = "yrpc"
) %>% select(
  reporter_iso,
  partner_iso,
  product_code,
  product_shortname_english,
  export_value_usd,
  import_value_usd
) %>% filter(reporter_iso != partner_iso)

write.csv(df, '/Users/karinabartolome/Documents/Analisis/datos_comercio/df.csv')


