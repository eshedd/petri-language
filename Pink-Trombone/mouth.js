const ws = new WebSocket("ws://localhost:5678/");
var recorder;
var buffer;
function prepareMouth() {
    pinkTromboneElement.pinkTrombone.context = pinkTromboneElement.pinkTrombone.audioContext
    recorder = new Recorder(pinkTromboneElement.pinkTrombone)
    window.addEventListener("keypress", event => {

        baseFrequency = pinkTromboneElement.parameters.frequency.value;
        //window.sayUKATON();
        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 440).then(() => {
        //     say(12.9, 0.9, 0.5, 1, 0.7, 0.6, 880).then(() => {
        //         say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 120).then(shutUp)
        //     })
        // })

        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 120)
        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 200)
        // shutUp()
        say({ index: randomNumber(6, 35), diameter: randomNumber(1, 5) }, { index: randomNumber(-50, 50), diameter: randomNumber(-1, 35) }, randomNumber(0, 5), randomNumber(0.2, 3), randomNumber(0, 1), randomNumber(0, 1), randomNumber(20, 1000)).then(shutUp)
    })
};
function sendData() {
    recorder.getBuffer(e => {
        buffer = e[0];
        ws.send("S")
        ws.send(buffer);
    });
    recorder.clear();
}
ws.onmessage = async function (event) {
    if (event.data[0] == "M") {
        params = event.data.split('|').map(Number);
        recorder.record();
        await say({ index: params[0], diameter: params[1] }, { index: params[2], diameter: params[3] }, params[4], params[5], params[6], params[7], params[8]);
        recorder.stop();
        shutUp();
        sendData();
    }
};

