import six
from six.moves import _thread

import threading
import os
from time import perf_counter

import sys
import time
import logging
import gi

gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
gi.require_version("Gst", "1.0")

from gi.repository import Gst, GLib, GObject

logging.basicConfig(level=logging.DEBUG, format="[%(name)s] [%(levelname)8s] - %(message)s")
logger = logging.getLogger(__name__)

class GstPlayer:
    Gst.init(None)
    
    def __init__(self):
        self.playing = False
        self.loop = None
        print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
        print("ID of process running task 1: {}".format(os.getpid()))
        # Create gstreamer elements
        self.source = Gst.ElementFactory.make("appsrc", "source")
        self.demuxer = Gst.ElementFactory.make("qtdemux", "demuxer")
        self.parser = Gst.ElementFactory.make("h264parse", "parser")
        #self.video_queue = Gst.ElementFactory.make("queue", "video-queue")
        self.video_decoder = Gst.ElementFactory.make("openh264dec", "video-decoder")
        # self.video_decoder = Gst.ElementFactory.make("avdec_h264", "video-decoder")
        self.video_timeoverlay = Gst.ElementFactory.make("timeoverlay", "video-timeoverlay")
        self.video_scaler = Gst.ElementFactory.make("videoscale", "video-scaler")
        self.video_converter = Gst.ElementFactory.make("videoconvert", "video-converter")
        self.video_sink = Gst.ElementFactory.make("autovideosink", "video-output")

        # Create the empty pipeline
        self.pipeline = Gst.Pipeline.new("dash-player")
        if (not self.pipeline or not self.source or not self.demuxer 
            or not self.parser  or not self.video_decoder or not self.video_timeoverlay 
            or not self.video_scaler or not self.video_converter or not self.video_sink
        ):
            logger.error("One element could not be created. Exiting.\n")
            sys.exit(1)

        # we add all elements into the pipeline
        # appsrc | demuxer | parser | video-queue | video-decoder | video-timeoverlay |
        # video-scaler | video-converter | video-sink
        # self.video_queue,
        [self.pipeline.add(k) for k in [
            self.source, self.demuxer, self.parser,  
            self.video_decoder, self.video_timeoverlay, self.video_scaler, self.video_converter, self.video_sink]
        ]

        # we link the elements together
        # appsrc -> demuxer -> parser -> video-queue -> video-decoder -> video-timeoverlay
        # -> video-rate -> video-scaler -> video-sink
        ret = self.source.link(self.demuxer)
        #ret = ret and self.demuxer.link(self.parser)
        # ret = ret and self.parser.link(self.video_queue)
        ret = ret and self.parser.link(self.video_decoder)
        ret = ret and self.video_decoder.link(self.video_timeoverlay)
        ret = ret and self.video_timeoverlay.link(self.video_scaler)
        ret = ret and self.video_scaler.link(self.video_converter)
        ret = ret and self.video_converter.link(self.video_sink)
        
        if not ret:
            logger.error("Elements could not be linked.\n")
            self.pipeline.unref()
            sys.exit(1)

        # Connect to the pad-added signal
        self.demuxer.connect("pad-added", self.pad_added_handler)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._handle_message)

    # This function will be called by the pad-added signal
    def pad_added_handler(self, src, new_pad):
        logger.info(f"Received new pad '{new_pad.get_name()}' from '{src.get_name()}'.\n")

        # Check the new pad's type
        new_pad_caps = new_pad.get_current_caps()
        new_pad_struct = new_pad_caps.get_structure(0)
        new_pad_type = new_pad_struct.get_name()

        logger.info(f"It has type '{new_pad_type}'.\n")

        if new_pad_type.startswith('video/x-h264'):
            # We can now link this pad with the video-decoder sink pad
            sink_pad = self.parser.get_static_pad("sink")
        else:
            logger.info(f"It has type '{new_pad_type}' which is not raw audio/video. Ignoring.\n")
            return
        
        # If our converter is already linked, we have nothing to do here
        if sink_pad.is_linked():
            logger.info("We are already linked. Ignoring.\n")
            return

        # Attempt the link
        ret = new_pad.link(sink_pad)

        if ret == Gst.PadLinkReturn.OK:
            logger.info(f"Link succeded (type '{new_pad_type}').\n") 

    def _handle_message(self, bus, message):
        """Callback for status updates from GStreamer."""
        if message.type == Gst.MessageType.EOS:
            logger.info("End-Of-Stream reached.\n")
            # file finished playing
            self.pipeline.set_state(Gst.State.NULL)
            #self.playing = False
            # if self.finished_callback:
            #     self.finished_callback()
 
        elif message.type == Gst.MessageType.ERROR:
            # error
            self.pipeline.set_state(Gst.State.NULL)
            err, debug_info = message.parse_error()
            logger.error(f"Error received from element {message.src.get_name()}: {err.message}\n")
            logger.error(f"Debugging information: {debug_info if debug_info else 'none'}\n")
            #self.playing = False 
        elif message.type == Gst.MessageType.STATE_CHANGED:
                    # We are only interested in state-changed messages from the pipeline
                    if message.src == self.pipeline:
                        old_state, new_state, pending_state = message.parse_state_changed()
                        logger.info(f"Pipeline state changed from {Gst.Element.state_get_name(old_state)} to {Gst.Element.state_get_name(new_state)}:\n")

    def _get_state(self):
        """Returns the current state flag of the pipeline."""
        # gst's get_state function returns a 3-tuple; we just want the
        # status flag in position 1.
        return self.pipeline.get_state(Gst.CLOCK_TIME_NONE)[1]
    
    def play_segment(self):
        print("====================> Playing...")
        """Immediately begin playing the segments received.
        """
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.set_state(Gst.State.PLAYING)
        self.playing = True

    def play(self):
        """If paused, resume playback."""
        if self._get_state() == Gst.State.PAUSED:
            self.pipeline.set_state(Gst.State.PLAYING)
            self.playing = True

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = False

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def main_loop(self):
        print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
        print("ID of process running task 2: {}".format(os.getpid()))
        print('====================> Using MainLoop\n')
        while True:
            self.loop = GLib.MainLoop()
            self.loop.run()
            print('Saiu do loop!')
            global stop_threads
            if stop_threads:
                print('Stoping player thread')
                break
    
    def quit_loop(self):
        self.loop.quit()

    def run(self):
        """Start a new thread for the player."""

        """Call this function before trying to play any video with
        play_segment() or play().
        """
        print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
        print("ID of process running task 2: {}".format(os.getpid()))

        # If we don't use the MainLoop, messages are never sent.
        def start():
            print("Task 3 assigned to thread: {}".format(threading.current_thread().name))
            print("ID of process running task 3: {}".format(os.getpid()))
            print('====================> Using MainLoop\n')
            loop = GLib.MainLoop()
            loop.run()
            
 
        print('====================> Starting a new thread for the player\n')
        t = threading.Thread(target=start, name='thread_player')
        t.start()
        #_thread.start_new_thread(start, ())


    def getQueuedBytes(self):
        return self.source.get_property("current-level-bytes")
    
    def push(self, data, index):
        
        """ Push a buffer into the source. """
  
        buffer = Gst.Buffer.new_wrapped(data)
        #gst_sample = Gst.Sample.new(buffer)
         #gst_flow_return = self._src.emit('push-sample', gst_sample)
        print("")
        print(f"==================> Pushing video segment {index}")
        print("")
        gst_flow_return = self.source.emit('push-buffer', buffer)
        del buffer

        if gst_flow_return != Gst.FlowReturn.OK:
            print('We got some error, stop sending data')  
            
        #print("Current queued bytes inside appsrc: ", self.getQueuedBytes())

if __name__ == '__main__':
    stop_threads = False
    # print ID of current process
    print("ID of process running main program: {}".format(os.getpid()))
    
    # print name of main thread
    print("Main thread name: {}".format(threading.main_thread().name))

    p = GstPlayer()

    print('====================> Starting a new thread for the player\n')
    t = threading.Thread(target=p.main_loop, name='player_thread')
    t.start()
    
    #p.run()
    
    
    init_file = open("BigBuckBunny_2s_init.mp4", "rb")
    init_binary = init_file.read()
    init_file.close()

    list_of_segments = ["BigBuckBunny_1s1.m4s", "BigBuckBunny_1s2.m4s", "BigBuckBunny_1s3.m4s",
                        "BigBuckBunny_1s4.m4s", "BigBuckBunny_1s5.m4s", "BigBuckBunny_1s6.m4s", 
                        "BigBuckBunny_1s7.m4s"]
    index = 0

    qb = p.getQueuedBytes()
    started_playing = False

    print()
    print('appsrc buffer level (bytes): ', qb)
    print()

    for segment in list_of_segments:
        print('=====================> Getting chunk ', segment)
    
        segment_file = open(segment, "rb")
        segment_binary = segment_file.read()
        segment_file.close()

        data = init_binary + segment_binary

        index += 1

        # if p.getQueuedBytes() == 0 and started_playing:
        #     print('PAUSING')
        #     p.pause()

        p.push(data, index)
        
        if p.getQueuedBytes() > 0 and not started_playing:
            print('PLAYING')
            p.play_segment()
            t1_start = perf_counter()
            started_playing = True
        
        
        # if index == 5:
        #     qb = p.getQueuedBytes()
        #     print()
        #     print('Not played - appsrc buffer level (bytes): ', qb)
        #     print()
        #     p.play_segment()
        
        qb = p.getQueuedBytes()
        print()
        print('Played appsrc buffer level (bytes): ', qb)
        print()
        
        # while index == 4:
        #     p.pause()
        #     time.sleep(4)
        #     index += 1
        
        # p.play()
        time.sleep(1)

    qb = p.getQueuedBytes()
    print()
    print('appsrc buffer level (bytes): ', qb)
    print()
    
    t1_stop = perf_counter()

    print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
    p.play()

    # while True:
    #     qb = p.getQueuedBytes()
    #     print()
    #     print('appsrc buffer level (bytes): ', qb)
    #     print()
    #     time.sleep(1)



    # p.pause()
    # print('======================> End of segments')
    # print('======================> Buffering')
    # time.sleep(4)
    # list_of_segments = ["BigBuckBunny_2s8.m4s", "BigBuckBunny_2s9.m4s"]
    # index = 7

    # for segment in list_of_segments:
    #     print('=====================> Getting chunk...')
    #     print(segment)
    
    #     segment_file = open(segment, "rb")
    #     segment_binary = segment_file.read()
    #     segment_file.close()

    #     data = init_binary + segment_binary

    #     index += 1
    #     p.push(data, index)
    #     p.play()
    #     time.sleep(2)

    # print('======================> End of segments')
    # time.sleep(5)

    # p.quit_loop()
    # stop_threads = True
    # t.join()
    # print(t.is_alive())
    
    
