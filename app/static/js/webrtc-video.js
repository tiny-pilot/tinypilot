/**
 * See here for the Janus Gateway API reference:
 * https://janus.conf.meetecho.com/docs/JS.html
 *
 * Tip for easier local development:
 * - Call `Janus.init` with `{debug: "all"}` to turn on all internal logging.
 *   Make sure to set the log level in your browser to debug/verbose.
 * - Change the server URL to the address of your real device. (Friendly
 *   reminder, just in case: that doesn’t forward mouse and keyboard.)
 */

Janus.init({
  debug: "all", // TODO(jotaen) Set this to false when development done.
});

const WEBRTC_VIDEO_ELEMENT = document.getElementById("webrtc-output");

// TODO(jotaen) Change to real URL. Also, account for https (wss) on Pro.
const JANUS_URL = `ws://raspberrypi/janus/ws`;

const janus = new Janus({
  server: JANUS_URL,
  success: function () {
    attachToJanusPlugin();
  },
  error: function (error) {
    console.error("Failed to connect to Janus: " + error);
  },
});

function attachToJanusPlugin() {
  let janusPluginHandle = null;

  janus.attach({
    plugin: "janus.plugin.ustreamer",
    opaqueId: "tinypilot-" + Janus.randomString(8),

    /**
     * This callback is triggered when the ICE state for the PeerConnection
     * associated to the handle changes.
     * ICE = Interactive Connectivity Establishment
     * See https://developer.mozilla.org/en-US/docs/Glossary/ICE
     * @param {string} state E.g., "connected" or "failed".
     */
    iceState: function (state) {
      console.debug("ICE Connection State changed to: " + state);
    },

    /**
     * @param {object} pluginHandle The Janus plugin handle.
     */
    success: function (pluginHandle) {
      janusPluginHandle = pluginHandle;
      console.debug("TinyPilot successfully attached uStreamer plugin");

      // This makes the uStreamer plugin generate a webrtc offer that will be
      // received in the onmessage handler.
      janusPluginHandle.send({ message: { request: "watch" } });
    },

    error: function (error) {
      console.error("Failed to attach to uStreamer plugin: " + error);
    },

    /**
     * @param {object} msg
     * @param {object|null} jsep JSEP = JavaScript Session Establishment Protocol
     */
    onmessage: function (msg, jsep) {
      if (!jsep) {
        return;
      }
      janusPluginHandle.createAnswer({
        jsep: jsep,
        // Client only receives media and does not interact with data channels.
        media: { audioSend: false, videoSend: false, data: false },
        success: function (jsep) {
          // Send back the generated webrtc response.
          janusPluginHandle.send({
            message: { request: "start" },
            jsep: jsep,
          });
        },
        error: function (error) {
          console.error("failed to create answer SDP: " + error);
        },
      });
    },

    /**
     * @param {MediaStreamTrack} track https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack
     * @param {string} mid The Media-ID.
     * @param {boolean} added Whether a track was added or removed.
     */
    onremotetrack: function (track, mid, added) {
      console.debug(`Remote track changed. mid:"${mid}" added:"${added}`);
      if (!added) {
        WEBRTC_VIDEO_ELEMENT.srcObject = null;
        return;
      }
      // According to the examples/tests in the Janus repository, the track
      // object should be cloned.
      // https://github.com/meetecho/janus-gateway/blob/4110eea4568926dc18642a544718c87118629253/html/streamingtest.js#L249-L250
      const stream = new MediaStream();
      stream.addTrack(track.clone());
      WEBRTC_VIDEO_ELEMENT.srcObject = stream;
    },
  });
}
