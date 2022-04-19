/**
 * The initialization of the WebRTC Video stream from the Janus plugin.
 *
 * Import this as `type="module"`, to avoid polluting the global namespace.
 *
 * This file implicitly depends on the following libraries to be loaded into the
 * global namespace, in this order:
 * - WebRTC Adapter 8.1.1
 * - Janus Gateway 1.0.0
 *
 * See here for the Janus Gateway API reference:
 * https://janus.conf.meetecho.com/docs/JS.html
 */

// Parameters for the setup.
const config = {
  // Set to `true` to turn on all internal Janus logging. Make sure to set the
  // log level in your browser to debug/verbose.
  isDebug: false,

  // The hostname of the device. For development, you can replace this with the
  // hostname of your testing device.
  deviceHostname: location.host,

  // Whether the connection should be established with SSL.
  useSSL: location.protocol === "https:",

  // The number of seconds within which the watch request can be retried.
  watchRequestRetryTimeoutSeconds: 60,
};

// Initialize library.
Janus.init({
  debug: config.isDebug ? "all" : false,
});

// Establish connection to the server.
const janus = new Janus({
  server: `${config.useSSL ? "wss" : "ws"}://${config.deviceHostname}/janus/ws`,
  success: attachToJanusPlugin,
  error: function (error) {
    console.error("Failed to connect to Janus: " + error);
  },
});

function attachToJanusPlugin() {
  let watchRequestRetryExpiryTimestamp = null;
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
     * The plugin handle was successfully created and is ready to be used.
     * @param {object} pluginHandle The Janus plugin handle.
     */
    success: function (pluginHandle) {
      janusPluginHandle = pluginHandle;
      console.debug("Successfully created Janus plugin handle.");

      watchRequestRetryExpiryTimestamp =
        Date.now() + config.watchRequestRetryTimeoutSeconds * 1000;
      // This makes the uStreamer plugin generate a webrtc offer that will be
      // received in the onmessage handler.
      janusPluginHandle.send({ message: { request: "watch" } });
    },

    /**
     * The plugin handle was NOT successfully created
     * @param error
     */
    error: function (error) {
      console.error("Failed to create Janus plugin handle: " + error);
    },

    /**
     * A message/event has been received from the plugin.
     * @param {object} msg
     * @param {object|null} jsep JSEP = JavaScript Session Establishment Protocol
     */
    onmessage: function (msg, jsep) {
      // `503` indicates that the plugin is not ready to stream yet. Retry
      // the watch request, until the H.264 stream is available or the watch
      // request timeout has been reached.
      if (
        msg.error_code === 503 &&
        watchRequestRetryExpiryTimestamp > Date.now()
      ) {
        janusPluginHandle.send({ message: { request: "watch" } });
        return;
      }
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
     * A remote media track is available and ready to be consumed.
     * @param {MediaStreamTrack} track https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack
     * @param {string} mid The Media-ID.
     * @param {boolean} added Whether a track was added or removed.
     */
    onremotetrack: function (track, mid, added) {
      console.debug(`Remote track changed. mid:"${mid}" added:"${added}`);
      const videoElement = document.getElementById("webrtc-output");

      if (!added) {
        videoElement.srcObject = null;
        return;
      }

      // According to the examples/tests in the Janus repository, the track
      // object should be cloned.
      // https://github.com/meetecho/janus-gateway/blob/4110eea4568926dc18642a544718c87118629253/html/streamingtest.js#L249-L250
      const stream = new MediaStream();
      stream.addTrack(track.clone());
      videoElement.srcObject = stream;
    },
  });
}
