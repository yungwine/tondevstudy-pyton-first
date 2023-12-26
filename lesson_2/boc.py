from pytoniq_core import Builder, Cell, Slice, begin_cell


cell = begin_cell().store_uint(15, 32).store_address('EQCPCZU37-aComPLgaQBcOkevn4x5GJHSfZsFt6eF9DpHcw4').end_cell()

cell2 = begin_cell().store_ref(cell).end_cell()

print(cell2.to_boc())

cs = cell.begin_parse()

print(cs)
print(cs.preload_uint(32))
print(cs)
# address = cs.load_address()

# print(address)

print(cs)
