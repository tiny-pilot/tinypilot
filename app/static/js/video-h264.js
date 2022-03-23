// This code is extracted almost verbatim from
// https://github.com/tiny-pilot/tinypilot/blob/064a485883b0d4af82274ce4018ef7def796bb28/app/templates/custom-elements/remote-screen.html

var janus_handle = null;
Janus.init({debug: "all"});
var janus = new Janus({
  server: `ws://${location.host}/janus/ws`,
  success: function () {
    console.info("success");
    attachToJanusPlugin();
  },
  error: function (error) {
    console.info("error " + error);
  },
});

function attachToJanusPlugin() {
  janus.attach({
    plugin: "janus.plugin.ustreamer",
    opaqueId: "tinypilot-" + Janus.randomString(8),
    iceState: function (state) {
      console.info("ICE Connection State changed to: " + state);
    },
    success: function (handle) {
      janus_handle = handle;
      console.info("tinypilot attached to ustreamer plugin");

      // makes ustreamer plugin generate a webrtc offer (apparently called jsep in janus)
      // that will be received in the onmessage handler
      janus_handle.send({message: {request: "watch"}});
    },
    error: function (error) {
      console.error("failed to attach to ustreamer plugin: " + error);
    },
    onmessage: function (msg, jsep) {
      if (jsep) {
        janus_handle.createAnswer({
          jsep: jsep,
          // client only receives media and does not interact with datachannels
          media: {audioSend: false, videoSend: false, data: false},
          success: function (jsep) {
            // sends back the generated webrtc response
            janus_handle.send({
              message: {request: "start"},
              jsep: jsep,
            });
          },
          error: function (error) {
            console.error("failed to create answer SDP: " + error);
          },
        });
      }
    },
    onremotestream: function (stream) {
      var videoElement = document.getElementById("h264-stream-output");
      Janus.attachMediaStream(videoElement, stream);
    },
  });
}
