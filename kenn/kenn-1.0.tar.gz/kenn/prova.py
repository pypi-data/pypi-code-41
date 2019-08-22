from kenn import knowledge_base as kb
import tensorflow as tf

unary_z = tf.constant([[-5.0, 3.0, -2.0],
           [3.0, 1.0, 0.0],
           [-2.0, 2.0, 1.0]])

binary_z = tf.constant([[-1.0, 0.0, 0.0],
                        [6.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0]])

uc, bc = kb.read_relational_knowledge_base('prova_kb', initial_clause_weight=1.0)
g1, g2, s1, s2 = kb.index_generator_simmetric(3)

udeltas = kb.knowledge_enhancer(unary_z, uc)

bm = kb.big_matrix_simmetric(unary_z, binary_z, g1, g2)
bdeltas = kb.knowledge_enhancer(bm, bc)
ufinal, bfinal = kb.project_deltas_simmetric(3, unary_z + udeltas, binary_z, bdeltas, s1, s2)

uip = tf.sigmoid(unary_z)
bip = tf.sigmoid(binary_z)

up = tf.sigmoid(ufinal)
bp = tf.sigmoid(bfinal)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    u, b = sess.run([ufinal, bfinal])

    print(u)
    print(b)

    print('predictions:')
    ui, u, bi, b = sess.run([uip, up, bip, bp])

    print('===============')
    print('initial u:')
    print(ui)
    print('final u:')
    print(u)

    print('===============')
    print('initial b:')
    print(bi)
    print('final b:')
    print(b)