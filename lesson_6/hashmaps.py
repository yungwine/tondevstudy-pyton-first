from pytoniq_core import HashMap, begin_cell, Address, Builder


def key_serializer(src):
    return len(src)


def value_serializer(src, dest):
    dest.store_uint(src, 32)


# hashmap = HashMap(32, key_serializer=lambda src: len(src))
# hashmap = HashMap(32, key_serializer=key_serializer, value_serializer=lambda src, dest: dest.store_uint(src, 32))
hashmap = HashMap(32, value_serializer=value_serializer)


hashmap.set(1, 4)
hashmap.set(2, 5)
hashmap.set(3, 6)

# hashmap.set('abc', begin_cell().store_uint(1, 32).end_cell())
# hashmap.set('abcd', begin_cell().store_uint(1, 32).end_cell())

# hashmap.set('abc', 1)
# hashmap.set('abcd', 2)


hashmap_cell = hashmap.serialize()
print(hashmap_cell)


def key_deserializer(src):
    return int(src, 2)


parsed_hashmap = HashMap.parse(hashmap_cell.begin_parse(), 32, key_deserializer=key_deserializer, value_deserializer=lambda src: src.load_uint(32))
print(parsed_hashmap)


hashmap2 = HashMap(267, value_serializer=lambda src, dest: dest.store_uint(src, 32))

(hashmap2
 .set(key=Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG'), value=15)
 .set(key=Address('EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N'), value=10)
 )

hashmap2_cell = hashmap2.serialize()


def key_deserializer2(src):
    return Builder().store_bits(src).end_cell().begin_parse().load_address()


parsed_hashmap2 = HashMap.parse(hashmap2_cell.begin_parse(), 267, key_deserializer=key_deserializer2, value_deserializer=lambda src: src.load_uint(32))

print(parsed_hashmap2)

hashmap2_slice = hashmap2_cell.begin_parse()

print(hashmap2_slice.load_hashmap(267, key_deserializer=key_deserializer2, value_deserializer=lambda src: src.load_uint(32)))

c = begin_cell().store_dict(hashmap2_cell).end_cell()
print(c.begin_parse().load_bit())
print(c.begin_parse().load_dict(267, key_deserializer=key_deserializer2, value_deserializer=lambda src: src.load_uint(32)))

c2 = begin_cell().store_bit_int(0).end_cell()
print(c2.begin_parse())
print(c2.begin_parse().load_dict(256))
