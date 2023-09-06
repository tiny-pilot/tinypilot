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
 *
 * See here for a high-level overview of the control flow:
 * https://github.com/tiny-pilot/ustreamer/blob/master/docs/h264.md
 */

// Suppress ESLint warnings about undefined variables.
// Janus is defined by the Janus library, which is globally available on the
// page.
/* global Janus */

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

// Get a handle on the global remote-screen element.
const remoteScreen = document.getElementById("remote-screen");

// Establish connection to the server.
const janus = new Janus({
  server: `${config.useSSL ? "wss" : "ws"}://${config.deviceHostname}/janus/ws`,
  success: attachToJanusPlugin,

  /**
   * This callback is triggered if either the initial connection couldn’t be
   * established, or if an established connection is interrupted.
   */
  error: function (error) {
    console.error("Connection to Janus failed: " + error);
    remoteScreen.enableMjpeg();
  },
});

/**
 * Asks the Janus server to initialize the uStreamer Janus plugin and to start
 * streaming the remote screen video.
 *
 * After the Janus server was started up, the uStreamer Janus plugin is NOT
 * loaded yet. Janus doesn’t initialize the plugin right away, but this will
 * only happen when the first client asks for it. After the plugin was loaded
 * for the first time, the server state is permanently altered.
 */
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
     * @param {string} state - E.g., "connected" or "failed".
     */
    iceState: function (state) {
      console.debug("ICE Connection State changed to: " + state);
    },

    /**
     * The plugin handle was successfully created and is ready to be used.
     * @param {Object} pluginHandle - The Janus plugin handle.
     */
    success: function (pluginHandle) {
      janusPluginHandle = pluginHandle;
      console.debug("Successfully created Janus plugin handle.");

      watchRequestRetryExpiryTimestamp =
        Date.now() + config.watchRequestRetryTimeoutSeconds * 1000;
      // Sending a `watch` request makes the uStreamer plugin generate a webRTC
      // offer that will be received in the `onmessage` handler.
      // Note, that the plugin will automatically start streaming when it
      // receives this request, so it’s technically not required to issue
      // another `start` request afterwards. (See below.)
      janusPluginHandle.send({
        message: { request: "watch", params: { audio: true } },
      });
    },

    /**
     * The plugin handle was NOT successfully created.
     * @param error
     */
    error: function (error) {
      console.error("Failed to create Janus plugin handle: " + error);
    },

    /**
     * A message/event has been received from the plugin.
     * @param {Object} msg
     * @param {Object} [jsep] - (JavaScript Session Establishment Protocol)
     */
    onmessage: function (msg, jsep) {
      // `503` indicates that the plugin was not initialized yet and therefore
      // isn’t ready to stream yet. We retry the watch request, until either the
      // H.264 stream is available, or the watch request timeout has been
      // reached.
      if (
        msg.error_code === 503 &&
        watchRequestRetryExpiryTimestamp > Date.now()
      ) {
        janusPluginHandle.send({
          message: { request: "watch", params: { audio: true } },
        });
        return;
      }
      if (!jsep) {
        return;
      }
      janusPluginHandle.createAnswer({
        jsep: jsep,
        // Disable sending audio and video (which would otherwise default to
        // `true`), to prevent the browser from presenting a permission dialog
        // to the user.
        media: { audioSend: false, videoSend: false },
        success: function (jsep) {
          // Send back the generated webRTC response. We technically don’t have
          // to send a `start` request for starting the stream, as the plugin
          // already starts streaming after the `watch` request. However,
          // without a `start` request, the server complains about the request
          // being malformed, which we want to avoid out of “good practice”.
          janusPluginHandle.send({
            message: { request: "start" },
            jsep: jsep,
          });
        },
        error: function (error) {
          console.error("Failed to create JSEP answer: " + error);
        },
      });
    },

    /**
     * The availability of a remote media track has changed – i.e. it was either
     * added or removed.
     *
     * Note: for the case that the media track was removed (e.g. due to a
     * network interruption, or the Janus backend server having failed), it’s
     * not safe to assume that this callback will be invoked reliably. We have
     * also observed different behavior in Chrome and Firefox.
     *
     * @param {MediaStreamTrack} track - https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack
     * @param {string} mid - The Media-ID.
     * @param {boolean} added - Whether the track was added or removed.
     */
    onremotetrack: async function (track, mid, added) {
      console.debug(
        `Remote ${track.kind} track "${mid}" ${added ? "added" : "removed"}.`
      );

      if (added) {
        await remoteScreen.addWebrtcStreamTrack(track);
        if (!remoteScreen.webrtcEnabled) {
          await remoteScreen.enableWebrtc();
        }
      } else {
        await remoteScreen.removeWebrtcStreamTrack(track);
      }
    },
  });
}
