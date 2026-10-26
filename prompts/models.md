# Каталог моделей Samsung TV 2024

Поколение «D» (2024). Для каждой модели: класс, диагонали, панельные характеристики, вилка цен для российского рынка, кому подойдёт, честные ограничения. Цены — ориентир для РФ-рынка 2024, вилки, не точные котировки, допустимо округление. Правила честности: Samsung не поддерживает Dolby Vision (только HDR10 и HDR10+); Crystal UHD — это обычная LED-подсветка, НЕ QLED; у 8K-моделей собственного 8K-контента почти нет, работает upscaling с 4K.

```toml
[[models]]
code = "QN90D"
trade_name = "Neo QLED QN90D"
tv_class = "neo_qled"
diagonals_inches = [43, 50, 55, 65, 75, 85]
refresh_hz = 120
brightness_nits_min = 1500
brightness_nits_max = 2000
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "mini_led"
price_min = 85000
price_max = 450000
fits_short = "Светлая гостиная, спорт и игры, яркое помещение"
honest_caveats = "Нет Dolby Vision; поддержка HDR10+ и HDR10"

[[models]]
code = "QN85D"
trade_name = "Neo QLED QN85D"
tv_class = "neo_qled"
diagonals_inches = [55, 65, 75, 85]
refresh_hz = 120
brightness_nits_min = 800
brightness_nits_max = 1200
hdmi_version = "2.1"
hdmi_ports = 2
backlight = "mini_led"
price_min = 80000
price_max = 200000
fits_short = "Средний топ Neo QLED, универсальный под кино и игры"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; только 2 порта HDMI 2.1 из 4"

[[models]]
code = "QN900D"
trade_name = "Neo QLED 8K QN900D"
tv_class = "neo_qled"
diagonals_inches = [65, 75, 85]
refresh_hz = 240
brightness_nits_min = 2000
brightness_nits_max = 4000
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "mini_led"
price_min = 350000
price_max = 900000
fits_short = "Флагман 8K без компромиссов, большая гостиная"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; собственного 8K-контента почти нет, работает upscaling с 4K"

[[models]]
code = "QN95D"
trade_name = "Neo QLED QN95D"
tv_class = "neo_qled"
diagonals_inches = [55, 65, 75, 85]
refresh_hz = 144
brightness_nits_min = 1600
brightness_nits_max = 2000
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "mini_led"
price_min = 150000
price_max = 400000
fits_short = "Топ 4K Neo QLED, внешний One Connect-блок, светлая гостиная"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+"

[[models]]
code = "S95D"
trade_name = "OLED S95D"
tv_class = "oled"
diagonals_inches = [55, 65, 77]
refresh_hz = 144
brightness_nits_min = 1000
brightness_nits_max = 1500
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "oled"
price_min = 190000
price_max = 500000
fits_short = "Кино в тёмной или полутёмной комнате, матовый экран без бликов"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; пики яркости только в HDR, в SDR заметно ниже"

[[models]]
code = "S90D"
trade_name = "OLED S90D"
tv_class = "oled"
diagonals_inches = [42, 48, 55, 65, 77, 83]
refresh_hz = 144
brightness_nits_min = 800
brightness_nits_max = 1300
hdmi_version = "2.1"
hdmi_ports = 4
backlight = "oled"
price_min = 100000
price_max = 350000
fits_short = "Доступный OLED, кино и игры, тёмная или полутёмная комната"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; тип панели (WOLED/QD-OLED) зависит от диагонали"

[[models]]
code = "Q80D"
trade_name = "QLED Q80D"
tv_class = "qled"
diagonals_inches = [50, 55, 65, 75, 85]
refresh_hz = 120
brightness_nits_min = 500
brightness_nits_max = 700
hdmi_version = "2.1"
hdmi_ports = 2
backlight = "full_array_led"
price_min = 75000
price_max = 170000
fits_short = "Средний QLED с полноматричной подсветкой, универсальный просмотр"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; 2 порта HDMI 2.1 из 4"

[[models]]
code = "Q70D"
trade_name = "QLED Q70D"
tv_class = "qled"
diagonals_inches = [55, 65, 75, 85]
refresh_hz = 120
brightness_nits_min = 350
brightness_nits_max = 500
hdmi_version = "2.1"
hdmi_ports = 2
backlight = "dual_led"
price_min = 65000
price_max = 150000
fits_short = "Бюджетный QLED, базовые игры и кино в умеренно светлой комнате"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; Dual LED-подсветка без локального затемнения"

[[models]]
code = "Q60D"
trade_name = "QLED Q60D"
tv_class = "qled"
diagonals_inches = [43, 50, 55, 65, 75, 85]
refresh_hz = 60
brightness_nits_min = 300
brightness_nits_max = 400
hdmi_version = "2.0"
hdmi_ports = 3
backlight = "edge_led"
price_min = 55000
price_max = 130000
fits_short = "Входной QLED, фильмы и сериалы без игр"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; HDMI 2.0 и панель 60Hz — не для PS5/Xbox в 120 fps"

[[models]]
code = "DU8000"
trade_name = "Crystal UHD DU8000"
tv_class = "crystal_uhd"
diagonals_inches = [43, 50, 55, 65, 75, 85]
refresh_hz = 60
brightness_nits_min = 300
brightness_nits_max = 350
hdmi_version = "2.0"
hdmi_ports = 3
backlight = "edge_led"
price_min = 45000
price_max = 110000
fits_short = "Бюджет для спальни, кухни или второго ТВ"
honest_caveats = "Нет Dolby Vision; Crystal UHD — это обычная LED-подсветка, НЕ QLED; HDMI 2.0 и панель 60Hz"

[[models]]
code = "DU7100"
trade_name = "Crystal UHD DU7100"
tv_class = "crystal_uhd"
diagonals_inches = [50, 55, 65, 75]
refresh_hz = 60
brightness_nits_min = 250
brightness_nits_max = 300
hdmi_version = "2.0"
hdmi_ports = 3
backlight = "edge_led"
price_min = 40000
price_max = 80000
fits_short = "Бюджет-линейка Crystal UHD, детская или второй ТВ"
honest_caveats = "Нет Dolby Vision; Crystal UHD — это обычная LED-подсветка, НЕ QLED; HDMI 2.0 и панель 60Hz"

[[models]]
code = "DU7000"
trade_name = "Crystal UHD DU7000"
tv_class = "crystal_uhd"
diagonals_inches = [43, 50, 55, 65, 75, 85]
refresh_hz = 60
brightness_nits_min = 250
brightness_nits_max = 300
hdmi_version = "2.0"
hdmi_ports = 3
backlight = "edge_led"
price_min = 35000
price_max = 80000
fits_short = "Самый бюджетный Crystal UHD, базовый ТВ в комнату или на кухню"
honest_caveats = "Нет Dolby Vision; Crystal UHD — это обычная LED-подсветка, НЕ QLED; HDMI 2.0 и панель 60Hz"

[[models]]
code = "LS03D"
trade_name = "The Frame LS03D"
tv_class = "lifestyle"
diagonals_inches = [32, 43, 50, 55, 65, 75, 85]
refresh_hz = 120
brightness_nits_min = 300
brightness_nits_max = 500
hdmi_version = "2.1"
hdmi_ports = 2
backlight = "edge_led"
price_min = 85000
price_max = 350000
fits_short = "Лайфстайл-рамка в интерьер, работает как картина в выключенном режиме"
honest_caveats = "Нет Dolby Vision; HDR10 и HDR10+; матовый экран снижает пиковую яркость; HDMI 2.1 только на 2 портах"
```

## Neo QLED QN90D

Флагманский 4K Neo QLED с mini-LED подсветкой и 120 Гц. Хорошо тянет яркую гостиную с окнами, спорт и игры с PS5/Xbox Series X: все 4 HDMI — 2.1 с поддержкой 4K@120, VRR и ALLM. Пиковая яркость 1500–2000 нит в HDR вытягивает блики на солнце и снег. Честно: Dolby Vision нет, у Samsung только HDR10 и HDR10+. Если смотрят Apple TV+/Netflix в HDR — пойдёт HDR10+, не Dolby Vision.

## Neo QLED QN85D

Средний топ Neo QLED: тоже mini-LED, но зон локального затемнения меньше, чем на QN90D, и яркость скромнее (800–1200 нит). Универсальный выбор под кино, спорт и игры, если бюджет не тянет QN90D. Важная тонкость: из четырёх HDMI версия 2.1 — только на двух. Для одной консоли достаточно, но если у клиента PS5 + Xbox + саундбар с HDMI 2.1 — предупредите. Dolby Vision нет, HDR10 и HDR10+.

## Neo QLED 8K QN900D

Флагман без компромиссов: 8K-разрешение, mini-LED с тысячами зон локального затемнения, эффективная частота до 240 Гц, пики 2000–4000 нит. Выносной One Connect-блок — один тонкий кабель к экрану. Честно: 8K-контента в природе почти нет (ни стримингов, ни дисков), работает хороший upscaling с 4K; покупают ради «на вырост», размера от 75 дюймов и большой светлой гостиной. Dolby Vision нет.

## Neo QLED QN95D

Топовый 4K Neo QLED этого поколения: mini-LED, 144 Гц, 1600–2000 нит, внешний One Connect-блок как у 8K-флагмана. По картинке очень близок к QN90D, выигрывает за счёт блока с проводами и чуть лучшего ANR-покрытия. Все 4 HDMI — 2.1. Светлая большая гостиная, кино + игры + спорт в одном устройстве. Dolby Vision нет; HDR10 и HDR10+.

## OLED S95D

Флагман OLED Samsung: QD-OLED-панель, 144 Гц, пиковая яркость 1000–1500 нит в HDR. Главная фишка 2024 года — матовое антибликовое покрытие (OLED Glare Free), снимает отражения в светлой комнате, хотя сам OLED всё равно просит хотя бы приглушённого света для максимума. Идеален под кино, Apple TV+ и Netflix в HDR, PS5/Xbox с 4K@120. Dolby Vision нет (HDR10 и HDR10+). В SDR пиковая яркость заметно ниже, чем в HDR — учитывайте, если смотрят много обычного ТВ днём.

## OLED S90D

Доступный OLED: цена ниже S95D, картинка на уровне топовых OLED прошлого поколения. Тип панели зависит от диагонали — 42/48/77/83" часто WOLED, 55/65" чаще QD-OLED с заметно более яркими цветами; при разговоре с клиентом стоит уточнить конкретную диагональ. 144 Гц, 4×HDMI 2.1, 800–1300 нит пика в HDR. Кино и игры в тёмной или полутёмной комнате. Dolby Vision нет.

## QLED Q80D

Середнячок QLED: полноматричная LED-подсветка (Full Array Local Dimming) с небольшим числом зон, 120 Гц, 500–700 нит. Универсальный просмотр: сериалы, кино, спорт, нетребовательные игры. Из четырёх HDMI версия 2.1 — только на двух портах, учитывайте при подключении PS5/Xbox + саундбара. Dolby Vision нет, HDR10 и HDR10+.

## QLED Q70D

Бюджетный QLED с Dual LED-подсветкой: без локального затемнения, 120 Гц, 350–500 нит. Подойдёт под базовые игры (PS5/Xbox в 4K@120 на HDMI 2.1 держит, но контрастность хуже Q80D) и обычный просмотр в умеренно светлой комнате. Для кино в тёмной лучше смотреть ступенькой выше. Dolby Vision нет.

## QLED Q60D

Входной QLED: Edge LED-подсветка, панель 60 Гц, HDMI 2.0, 300–400 нит. Для фильмов, сериалов и ТВ-эфира — хватает. Для PS5/Xbox в 120 fps — не подойдёт, нужен HDMI 2.1 и 120 Гц. Хороший бюджетный ТВ в спальню или гостиную без игровых запросов. Dolby Vision нет; HDR10 и HDR10+.

## Crystal UHD DU8000

Старшая Crystal UHD линейка 2024. Честно: Crystal UHD — это обычная LED-подсветка (Edge LED), **не QLED** и не Neo QLED; маркетинговое название, а не технология квантовых точек. 60 Гц, HDMI 2.0, 300–350 нит. Хороший бюджетный выбор под спальню, кухню или второй ТВ, где не смотрят HDR-кино и не играют на PS5 в 120 fps. Dolby Vision нет.

## Crystal UHD DU7100

Средняя Crystal UHD линейка. Та же технология: обычная LED-подсветка (Edge LED), **не QLED**. 60 Гц, HDMI 2.0, 250–300 нит. Подходит под детскую, кухню, спальню — там, где важна цена и 4K-разрешение, но не нужны HDR-пики, 120 Гц или HDMI 2.1. Dolby Vision нет; HDR10 и HDR10+ в теории поддерживаются, но вытянуть их такая яркость всё равно не сможет.

## Crystal UHD DU7000

Самая бюджетная 4K-линейка Samsung 2024. Edge LED, 60 Гц, HDMI 2.0, 250–300 нит. Crystal UHD — это **не QLED**, обычная LED-подсветка. Для базового просмотра ТВ, сериалов, YouTube в небольшой комнате. Не для игр в 120 fps, не для HDR-кино с большими пиками яркости. Dolby Vision нет.

## The Frame LS03D

Лайфстайл-ТВ в формате картины: когда ТВ выключен, он показывает выбранное произведение искусства, встаёт в раму и вписывается в интерьер. QLED-матрица с матовым антибликовым покрытием, 120 Гц, пиковая яркость 300–500 нит. HDMI 2.1 только на двух портах из четырёх. Главный критерий покупки — эстетика, не чистая картинка; для кино в тёмной комнате OLED лучше, для яркой гостиной со спортом Neo QLED лучше. Dolby Vision нет; HDR10 и HDR10+.
