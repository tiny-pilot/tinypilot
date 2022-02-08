# WebRTC

The purpose of this document is to clarify the background mechanics of WebRTC and
explain the required network setup given different scenarios when wanting to connect to tinypilot.

## WebRTC Protocol

WebRTC uses a collection of protocols to establish direct peer-to-peer connections.
It does so without having to explicitly open any ports on a router (in case we are behind a NAT)
and the communication happens over UDP (and other protocols built on top of UDP).

For an overview of how STUN and TURN work please refer to [this document](https://www.frozenmountain.com/developers/blog/webrtc-nat-traversal-methods-a-case-for-embedded-turn).

# WebRTC

### Quick Overview

WebRTC is a peer-to-peer communication protocol composed of a set of internet protocols and NAT traversal techniques for establishing the connection.
The protocol can work on its own (without external servers) if there is a direct connection between peers (e.g. being in the same network or not being behind a NAT).
Otherwise, the protocol requires a STUN server (used for checking the public IP address) or sometimes even a TURN server (used for relaying the communication).
All communication (other than signaling) is done over some form of UDP.
Signaling is the term used for all communication that is not done directly via WebRTC.
Usually, these are messages there are required for establishing the initial connection and/or renegotiating parameters of the session.

### Connection Flow

This part describes how WebRTC works in general without actually mentioning the browser API.

A WebRTC connection starts when two peers are "signaled" to start a connection.
This "signal" can for example just be an http call or in most cases, a Websocket is used so that further messages can be exchanged.

Then, both peers start to check for Interactive Connectivity Exchange (ICE) Candidates.
These candidates are in essence just IP and Port pairs over which the other peer should attempt to connect with.

These candidates are found by multiple techniques.
One is checking the network interfaces for local IP addresses.
Another one is checking the public IP address with a STUN server.
And the "last resort" one is by specifying a TURN server that is accessible to both peers.

Before the candidate exchange happens both peers have to exchange Session Description Protocol (SDP) messages.
These messages contain the configuration for the connection, things like what media codecs the peer supports and if it will send media, and which type.
ICE candidates may also already be included in the SDP messages.
The initiating peer creates an Offer and sends it over the signaling channel to the other peer.
The other peer will add the received SDP to the peer connection configuration and generate a Response which it also sends back via the signaling channel.

After the ICE candidate gathering process has finished, the ICE candidates are exchanged through the signaling channel.
After being exchanged the peers attempt to connect with each other by sending packets to the IP:PORT pairs sent in the candidates.
If both peers succeed in sending packets to each other then the communication was established successfully.
In some cases, peers might not succeed in connecting because of the network conditions.
For example, no STUN server is specified and peers are not on the same network.
Or the type of NAT is symmetric on both sides which doesn't allow for a direct connection to be established so a TURN server is needed.
More details on how the NAT traversal techniques actually work can be found in this article: https://akiroz.medium.com/understanding-nat-traversal-for-webrtc-applications-64f492285340

Note: The flow I described does not necessarily have to be done in that exact order.
For example, one can choose to wait for all candidates to be gathered and only then send the SDP (in which the candidates will be included).
Or one can send the candidates as they are being gathered so one does not have to wait for all of them to be collected. This process is called trickle ICE.

After the ICE process is completed successfully the peers will set up the communication channels they configured in the SDP.
This is when the media and data channels are established. It is all the same UDP connection but it is multiplexed on application level.

### WebRTC Browser API

This part attempts to guide developers on how to use the browser WebRTC API by referencing the connection flow above.

The process starts when both peers create an [RTCPeerConnection](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection) object.
Once this object is instantiated it immediately initiates the ICE candidate gathering process.
Usually one would have an `onicecandidate` handler that would take care of sending the candidate to the remote peer,
but with the Janus client, this part is completely abstracted away.

Then the initiating peer would make a call to [`createOffer`](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/createOffer) and
send the result to the other peer via the signaling channel.
The other peer would add this offer by calling [`setRemoteDescription`](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/setRemoteDescription),
then it would call [`createAnswer`](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/createAnswer) and send the answer back to the
initiating peer which would make a call to `setRemoteDescription` itself.

This part is not completely abstracted by Janus since configuring the connection is done by the plugin (it sends that it will send an h264 stream).
So this part is handled [here](app/templates/custom-elements/remote-screen.html#L113) in tinypilot. For some reason, in Janus they call the SDP by JSEP.
In the `if (jsep)` block one can see the `createAnswer` call from the janus client which receives the JSEP directly.
It then makes the `setRemoteDescription` call internally and also sends the created answer directly back to Janus.
The Janus client is basically abstracting the WebRTC communication along with the whole signaling part.
After this succeeds the WebRTC communication to Janus has been established.

Because the plugin had configured the connection to have a media channel the receiving peer (the browser) can expect a call to [`onTrack`](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/onTrack) callback.
In Janus it is called `onremotestream`. Here we can just take the stream given in the function call and attach it to a `<video>` element.
Again, Janus abstracts this a bit and makes the "attaching" simpler with the `Janus.attachMediaStream` util function.

### STUN and TURN Notes

As mentioned above, sometimes these servers are necessary. Although in some cases one can choose to not use TURN servers.
In this section, I will attempt to explain under which of your common use cases you might need these servers.

#### Router Port is open and forwarding to Tinypilot

In this case, one must have a STUN server configured.
This is because without it tinypilot will only be able to find
its local IP addresses (the NAT translated ones) and these won't be accessible over the internet.

With the STUN Server, both peers may find their public IP address and communicate over that.
However, there is a slight chance that both peers are behind symmetric NATs which will make the connection fail even with the public IP address.
In these cases, a TURN server is needed so that both peers can completely relay the connection over it.

#### Client connects over VPN

In this scenario, one would not need a STUN server since both peers would have local IP addresses inside the same network and would be able to communicate over that.

NOTE: This is only my understanding, I have never tested this scenario.

### Using STUN and TURN servers in the Tinypilot setup

There are publicly available STUN servers that can be used for this, most commonly I see this one be used: `stun:stun.l.google.com:19302`.

You can add different ones to the `iceServers` parameter of the Janus client instantiation call like this:
```
new Janus({iceServers: ['stun:stun.l.google.com:19302'], ...})
```
Apparently, the Janus client already uses this STUN server by default [here](app/static/js/janus.js#L565).
One must also set this on the tinypilot side in the janus call using the `--stun-server=address:port` flag.

TURN server addresses can be added to the same list. However, since TURN servers actually do some heavy lifting in terms of resources they are not publicly available.
Therefore, if you consider it necessary to set them up, you have to do it yourself.

I believe the most popular implementation of a TURN server is [coturn](https://github.com/coturn/coturn).
They have some documentation on how to set this up but it sounds a bit tricky and heavily depends on your deployment.
