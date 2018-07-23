import datetime, time
import os, sys
from collections import OrderedDict
from prettytable import PrettyTable

from peewee import SqliteDatabase, Model
from peewee import CharField, IntegerField, BooleanField, DateField
from peewee import fn

db = SqliteDatabase('booklist.db')



class Book(Model):
	owner = CharField()
	rank = IntegerField()
	title = CharField()
	author = CharField()
	genre = CharField()
	read = BooleanField(default=False)
	date_added = DateField(default=datetime.datetime.now)
	date_read = DateField(null=True, default=None)
	
	class Meta:
		database = db
		
		
# === SOME FUNCTIONS ===

def initialize():
	"""Create the database and the table if they don't exist"""
	db.connect()
	db.create_tables([Book], safe=True)
		
		
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')
		
#def menu_loop():

def main_menu_loop():
	"""Show the menu"""
	choice = None
	
	while choice not in ('q', 'quit', 'exit'):
		list_all()
		print("\n === main menu ===")
		for key, value in menu.items():
			print("  {}) {}".format(key, value.__doc__) if (len(key) == 1) else 
				  " {}) {}".format(key, value.__doc__))
		print("  q) Quit")
		choice = input("\nChoice:  ").lower().strip()
		
		if choice in menu:
			menu[choice]()
			
def pretty_table(q, owner):
	"""Creates pretty table"""
	rows = []
	for __ in q:
		rows.append([__.rank, __.title, __.author, __.genre])

	print("\n| {}'s List |".format(owner))

	col_names = ['rank', 'title', 'author', 'genre']

	x = PrettyTable(col_names)
	# x.align[col_names[1]] = 'l'
	# x.align[col_names[2]] = 'l'
	x.padding_width = 1
	for row in rows:
		x.add_row(row)
	print(x)
			
			
# === MENU OPTIONS ===

owners_list = ['Finch', 'Amy', 'Shawn']

def add_book():
	"""Add a book"""
	while True:
		inp = input("Whose book is this?  ").title()
		if inp in owners_list:
			owner_ = inp
			break
		else:
			print("I don't know that person!")
	
	title_ = input("Title:  ")
	author_ = input("Author:  ")
	genre_ = input("Genre:  ")
	
	list_all()
	rank_ = input("Rank:  ")
	
	if input("Are you sure you want to add \"{}\"? (Y/n):  "
		.format(title_)).lower() != 'n':
		
		if (Book.select()
			  .where((Book.owner == owner_) & (Book.rank == rank_))
			  .count() > 0):
			q = (Book.update(rank=Book.rank + 1)
				 .where((Book.owner == owner_) & (Book.rank >= rank_)))
			q.execute()
			
		Book.create(owner=owner_,
					 title=title_,
					 author=author_,
					 genre=genre_,
					 rank=rank_)
		list_all()
	

def list_all():
	"""List all"""
	def query(owner):
		return ((Book.select()
				 .where(Book.owner == owner)
				 .order_by(Book.rank)), owner)

	clear()
	for each in owners_list:
		pretty_table(*query(each))


def del_book():
	"""Delete a book"""
	list_all()
	inp = input("Enter title of book to delete:  ")
	d = Book.get(Book.title == inp)
	if input("Are you sure you want to DELETE \"{}\"? (y/N):  "
		.format(d.title)).lower() == 'y':
		q = (Book.update(rank=Book.rank - 1)
			 .where(Book.rank >= d.rank))
		q.execute()
		d.delete_instance()


def edit_menu_loop():
	"""Edit book"""
	def edit_apply(row, field):
		cur_value = getattr(row, field)
		print("Current {}: {}".format(field, cur_value))
		new_value = input("New {}:  ".format(field))
		
		if field == 'rank':
			new_value = int(new_value)
			
			if new_value > cur_value:
				q = (Book.update(rank=Book.rank - 1)
					 .where((Book.owner == row.owner) & 
							(Book.rank > cur_value) &
							(Book.rank <= new_value)))
				q.execute()
			
			elif new_value < cur_value:
				q = (Book.update(rank=Book.rank + 1)
					 .where((Book.owner == row.owner) & 
							(Book.rank < cur_value) &
							(Book.rank >= new_value)))
				q.execute()
		
		setattr(row, field, new_value)
		row.save()
		
	list_all()
	inp = input("Enter title of book to edit:  ")
	row = Book.get(Book.title == inp)
	
	choice = None
	
	while choice not in ('x', 'exit'):
		list_all()
		print("\n === edit menu === {} ===".format(row.title))
		for key, value in edit_menu.items():
			print(" {})  {}".format(key, value))
		print(" x)  Exit to main menu")
		choice = input('\nChoice:  ').lower().strip()
		
		if choice in edit_menu:
			edit_apply(row, edit_menu[choice])


def list_selection():
	"""List selection"""
	global tq
	global gq

	if selections['t'] == "*":
		tq = (Book.rank != 666)
	else:
		tq = (Book.rank <= selections['t'])

	if selections['g'] == "*":
		gq = (Book.genre != "godisuck")
	else:
		gq = (Book.genre == selections['g'])
	


	def query(owner):
		return ((Book.select()
				 .where((Book.owner == owner) &
		 				gq & tq)
				 .order_by(Book.rank)), owner)

	clear()
	for each in owners_list:
		pretty_table(*query(each))


def bookpick_menu_loop():
	"""Bookpick Menu"""
	choice = None
	
	while choice not in ('x', 'exit'):
		list_selection()
		print("\n === bookpick menu ===")
		for key, value in bookpick_menu.items():
			print("  {}) {}  ({})".format(key, value.__doc__, selections[key]))
		print(" ------------------")
		print("  p) Pick a Book!")
		print(" ------------------")
		print("  c) Clear all selections")
		print("  x) Exit to main menu")
		choice = input('\nChoice:  ').lower().strip()
		
		if choice in bookpick_menu:
			bookpick_menu[choice]()
		elif choice == "c":
			selections['t'] = "*"
			selections['g'] = "*"
		elif choice == "p":
			bookpick_go()

def choose_genre():
	"""Choose genre"""
	list_selection()
	selections['g'] = input("Pick genre ('*' for all):  ")

def choose_top():
	"""Choose top #"""
	list_selection()
	selections['t'] = input("Pick top # ('*' for all):  ")

# def toggle_avail():
# 	"""Available"""
# 	if selections['v'] == False:
# 		selections['v'] = True
# 	else:
# 		selections['v'] = False

def test_func():
	"""Test function"""
	pass

def bookpick_go():
	"""Pick a Book!"""

	pick = ((Book.select()
			 .where(gq & tq)
			 .order_by(fn.Random()).limit(1))
			 .get())
	clear()
	print("\n")
	for c in "========= Your pick is =========":
		sys.stdout.write( '%s' % c )
		sys.stdout.flush()
		time.sleep(0.05)
	print("\n\n" + pick.title.upper().center(32," "))
	print("\n" + pick.author.center(32," "))
	print("\n================================")
	input(">")


# === LISTS ===
# owners = 'pass'
selections = {
	't': "*",
	'g': "*",
}

# === MENUS ===
menu = OrderedDict([
		('a', add_book),
		('d', del_book),
		('e', edit_menu_loop),
#		('la', list_all),
		('p', bookpick_menu_loop),
#		('lw', list_read),
#		('test', test_func),
	])

edit_menu = OrderedDict([
		('r', 'rank'),
		('t', 'title'),
		('g', 'genre'),
#		('w', 'read')
	])

bookpick_menu = OrderedDict([
		('t', choose_top),
		('g', choose_genre),
	])

# === MAIN ===
if __name__ == '__main__':
	initialize()
	main_menu_loop()