import tensorflow as tf
import os 

def train(batches,path,save_every=1000,max_steps=200000):
    """
    train a model, tensorflow's default graph
    """
    train_op=tf.get_collection("train_op")[0]
    global_step=tf.get_collection("global_step")[0]
    summary=tf.get_collection("summary")[0]
    loss=tf.get_collection("loss")[0]
    inputs=tf.get_collection("inputs")
    targets=tf.get_collection("targets")

    run_ops=[train_op,loss,global_step,summary]

    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth=True


    with tf.Session(config=config) as sess:


        saver=tf.train.Saver()

        if os.path.exists(path) and tf.train.latest_checkpoint(path) is not None:
            checkpoint=tf.train.latest_checkpoint(path)
            saver.restore(sess,checkpoint)
            print("restore from {}".format(checkpoint))
        else:
            init_op=tf.global_variables_initializer()
            print(init_op)
            sess.run(init_op)
            os.makedirs(path,exist_ok=True)

        log_dir=os.path.join(path,"logs")
        summary_writer=tf.summary.FileWriter(log_dir,tf.get_default_graph())

        start_time=time.time()
        for batch in batches:
            batch_time=time.time()-start_time
            start_time=time.time()
            feed_dict=dict(zip(inputs+targets,batch))
            _,loss,current_step,summary=sess.run(run_ops,feed_dict=feed_dict)
            summary_writer.add_summary(summary,current_step)
            """
            if current_step%100==0:
                y,current_step,summary=self.sess.run([output,global_step,valid_summary],feed_dict={input_:x})
                summary_writer.add_summary(summary,current_step)
            """
            if current_step%save_every==0:
                tmp_checkpoint=path+"/step-{}".format(current_step)
                saver.save(sess,tmp_checkpoint)
                print("saved to {}".format(tmp_checkpoint))

            if current_step==max_steps:
                break

            step_time=time.time()-start_time
            print("step {}, batch-time:{:.5f}, train-time:{:.5f}, loss: {:.4f} ".format(current_step,batch_time,step_time,loss),flush=True)
            start_time=time.time()


def predict(feeds,path):
    inputs=tf.get_collection("inputs")
    outputs=tf.get_collection("outputs")
    with tf.Session() as sess:
        saver=tf.train.Saver()
        checkpoint=tf.train.latest_checkpoint(path)
        assert checkpoint is not None
        saver.restore(sess,checkpoint)
        print("restore from {}".format(checkpoint))

        feed_dict=dict(zip(inputs,feeds))
        outputs=sess.run(outputs,feed_dict=feed_dict)
        return outputs
