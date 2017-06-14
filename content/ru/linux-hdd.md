Title: Подключение нового жесткого диска в Linux
Date: 2010-11-26 21:14
Author: Admin
Category: Linux
Tags: Linux, администрирование
Lang: ru

Доброго времени суток, товарищи линуксоиды!!

В этой статье я хочу рассказать о процессе подключения нового жёсткого
диска в ОС Linux.

Подключив жёсткий диск убедитесь, что система распознаёт его. Для этого
можно обратиться к программе конфигурации BIOS. Убедившись в том что
жёсткий диск успешно подключён можно приступать к загрузке системы.

Сразу после загрузки необходимо проверить существует ли файл устройств
для нового диска. В Linux жёсткие диски обозначаются в формате
/dev/sdXN, где X — буква латинского алфавита, означает диск, а N номер
раздела на жёстком диске.

Убедившись в том что файл устройства существует можно приступать к
разбивке диска на разделы. В моём случае файл устройства называется
/dev/sdb, т.к. это второй диск в системе (первый как вы наверное
догадались /dev/sda).

Итак для создания разделам будем использовать утилиту fdisk.

	:::bash
	fdisk /dev/sdb

	:::text
	Device contains neither a valid DOS partition table, nor Sun, SGI or OSF disklabel
	Building a new DOS disklabel with disk identifier 0x07611c35.
	Changes will remain in memory only, until you decide to write them.
	After that, of course, the previous content won't be recoverable.
	The number of cylinders for this disk is set to 60801.
	There is nothing wrong with that, but this is larger than 1024,
	and could in certain setups cause problems with:
	1) software that runs at boot time (e.g., old versions of LILO)
	2) booting and partitioning software from other OSs
	(e.g., DOS FDISK, OS/2 FDISK)
	Warning: invalid flag 0x0000 of partition table 4 will be corrected by w(rite)

Утилита выводит информацию о жёстком диске: идентификатор диска,
количество цилиндров. Потом она ожидает ввода команды, для вывода
справочной информации о всех доступных командах введите m. Мы будем
использовать три инструкции:

`n (new)` - создать новый раздел.

`p (print)` - вывести информацию о разделах

`w (write)` — записать таблицу разделов на диск

Я создам только один раздел, который будет занимать весь доступный объём
диска. Для этого я ввожу команду new, номер раздела 1, первый цилиндр 1
и последний цилиндр 60801 (значение по умолчанию). Если вы хотите
создать большее количество разделов, то просто аналогичным образом
добавьте необходимое количество разделов. Размер раздела можно задавать
в цилиндрах, как в показанном примере, или более простым способом, в
байтах (мегабайтах или гигабайтах) .

	:::text
	Command (m for help): new
	Command action
	e extended
	p primary partition (1-4)
	p
	Partition number (1-4): 1
	First cylinder (1-60801, default 1): 1
	Last cylinder or +size or +sizeM or +sizeK (1-60801, default 60801):
	Using default value 60801

Выводим информацию о разделах при помощи команды print.

	:::text
	Command (m for help): print

	Disk /dev/sdb: 500.1 GB, 500107862016 bytes
	255 heads, 63 sectors/track, 60801 cylinders
	Units = cylinders of 16065 * 512 = 8225280 bytes
	Disk identifier: 0x07611c35

	Device Boot Start End Blocks Id System
	/dev/sdb1 1 60801 488384001 83 Linux

Убедившись что разделы созданы так как вы рассчитывали записываем
таблицу разделов на диск при помощи команды `write`.

	:::text
	Command (m for help): write
	The partition table has been altered!
	Calling ioctl() to re-read partition table.
	Syncing disks.

Теперь можно приступить к форматировании разделов.

Для этого мы будем использовать команду `mke2fs -j`, указав в качестве
аргумента имя раздела.

	:::bash
	mke2fs -j /dev/sdb1
	mke2fs 1.41.3 (12-Oct-2008)
	Filesystem label=
	OS type: Linux
	Block size=4096 (log=2)
	Fragment size=4096 (log=2)
	30531584 inodes, 122096000 blocks
	6104800 blocks (5.00%) reserved for the super user
	First data block=0
	Maximum filesystem blocks=0
	3727 block groups
	32768 blocks per group, 32768 fragments per group
	8192 inodes per group
	Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
	4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
	102400000

	Writing inode tables: done
	Creating journal (32768 blocks): done
	Writing superblocks and filesystem accounting information: done

	This filesystem will be automatically checked every 34 mounts or
	180 days, whichever comes first. Use tune2fs -c or -i to override.

Теперь необходимо настроить монтирование новых разделов. Сначала
создадим каталог, который мы будем использовать как точку монтирования.

	:::bash
	mkdir /media/mediahdd

Пробуем монтировать раздел.

	:::bash
	mount /dev/sdb1 /media/mediahdd

Теперь необходимо добавить информацию о новом разделе в файл `/etc/fstab`
для, того чтобы раздел автоматически монтировался при каждой загрузке
системы. Для этого открываем этот файл в любом текстовом редакторе.

	:::bash
	nano /etc/fstab

Добавляем строку формата: `имя_раздела` `точка_монтирования`
`файловая_система` `частота_создания_резервных_копий`
`кол-во_запусков_fsck`

	:::text
	/dev/sdb1 /media/mediahdd ext3 defaults 0 0
