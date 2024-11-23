src="https://cdn.socket.io/4.0.0/socket.io.min.js"


const socket = io();

socket.on("data_update", (data) => {
  document.getElementById("FlightMode").textContent = data.FlightMode;
  document.getElementById("GPSdata").textContent = data.GPSdata;
  document.getElementById("RCsignalstrength").textContent =
    data.RCsignalstrength;
  document.getElementById("Speed").textContent = data.Speed;
  document.getElementById("Altitude").textContent = data.Altitude;
  document.getElementById("Roll").textContent = data.Roll;
  document.getElementById("Pitch").textContent = data.Pitch;
  document.getElementById("Yaw").textContent = data.Yaw;
  document.getElementById("CurrentDraw").textContent = data.CurrentDraw;
  document.getElementById("MotorSpeed").textContent = data.MotorSpeed;
});

function changeFlightMode(mode) {
    console.log(`Changing flight mode to: ${mode}`);
    socket.emit("change_flight_mode", mode); // Emit an event to change flight mode (can be handled server-side)
    }
  
  // Function to handle text input
document.getElementById("textInput").addEventListener("change", (e) => {
    const text = e.target.value;
    console.log(`Text input: ${text}`);
    // Handle the text input, like sending it to the server or processing it
    });



// Create a new RTCPeerConnection instance
let pc = new RTCPeerConnection();

// Function to send an offer request to the server
async function newOffer() {
    console.log("Sending offer request");

    // Fetch the offer from the server
    const offerResponse = await fetch("/offer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            sdp: "",
            type: "offer",
        }),
    });

    // Parse the offer response
    const offer = await offerResponse.json();
    console.log("Received offer response:", offer);

    // Set the remote description based on the received offer
    await pc.setRemoteDescription(new RTCSessionDescription(offer));

    // Create an answer and set it as the local description
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
}

// Trigger the process by creating and sending an offer
newOffer();