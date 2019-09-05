from pipe_io import PipeIO


if __name__ == '__main__':
    with PipeIO('in', 'out') as pipeio:
        pipeio.reader.message_handler = pipeio.writer.send_message
        pipeio.reader.run()
