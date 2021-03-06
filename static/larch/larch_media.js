//-*************************
//-* This program is free software; you can use it, redistribute it and/or
//-* modify it under the terms of the GNU Affero General Public License
//-* version 3 as published by the Free Software Foundation. The full text of
//-* the GNU Affero General Public License version 3 can be found in the file
//-* named 'LICENSE.txt' that accompanies this program. This source code is
//-* (C)copyright Geoffrey French 2011-2014.
//-*************************


larch.media = {};

larch.media.hasGetUserMedia = function() {
    return !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia)
};




larch.media.__mergeAudioBuffers = function(channelBuffers, channelLength) {
    //
    //
    // ADAPTED FROM
    // http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
    //
    //
    var result = new Float32Array(channelLength);
    var pos = 0;
    var numBuffers = channelBuffers.length;
    for (var i = 0; i < numBuffers; i++){
        var buffer = channelBuffers[i];
        result.set(buffer, pos);
        pos += buffer.length;
    }
    return result;
};

larch.media.__interleaveAudioChannels = function(leftChannel, rightChannel){
    //
    //
    // ADAPTED FROM
    // http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
    //
    //
    var interleavedLength = leftChannel.length + rightChannel.length;
    var result = new Float32Array(interleavedLength);

    var inputIndex = 0;

    for (var index = 0; index < interleavedLength; ){
        result[index++] = leftChannel[inputIndex];
        result[index++] = rightChannel[inputIndex];
        inputIndex++;
    }
    return result;
};

larch.media.__writeStringToMemoryView = function(view, pos, string){
    //
    //
    // ADAPTED FROM
    // http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
    //
    //
    var lng = string.length;
    for (var i = 0; i < lng; i++){
        view.setUint8(pos + i, string.charCodeAt(i));
    }
};



// numChannels - number of channels - 1 or 2
// format:
//      'raw16': raw 16-bit
//      'raw8': raw 8-bit
//      'rawf32': raw 32-bit float
//      'wav' : 16-bit WAV file
// gotCaptureFn is a callback of the form function(capture_object) that is called when the user allows access to the audio capture
// deniedFn is a callback of the form function(capture_object) that is called when the user denies access to the audio capture
// startFn is a callback of the form function(capture_object) that is called when recording starts
// audioDataFn: function of the form function(capture_object, audioData)
//      audioData is a list of channels, each of which is a blob. Note that the 'wav' format only generates 1 blob, which is the WAV file

larch.media.audioCapture = function(numChannels, format, gotCaptureFn, deniedFn, startFn, audioDataFn) {
    //
    //
    // ADAPTED FROM
    // http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
    //
    //

    if (!larch.media.hasGetUserMedia()) {
        return null;
    }

    if (numChannels < 1  ||  numChannels > 2) {
        throw 'Unsuppored number of channels: ' + numChannels;
    }

    if (format !== 'raw16'  &&  format != 'raw8'  &&  format != 'rawf32'  &&  format != 'wav') {
        throw 'Unsuppored format: ' + format;
    }




    // Capture object

    var capture = {
        numChannels: numChannels,
        sampleRate: 44100,
        numSamples: 0,
        gotCapture: false,
        recording: false,
        __format: format,
        __channelBuffers: null,
        __sampleCount: 0,
        __recordingStream: null,
        __gotCaptureFn: gotCaptureFn,
        __deniedFn: deniedFn,
        __startFn: startFn,
        __audioDataFn: audioDataFn,

        // Initialise channel buffers
        __initChannelBuffers: function() {
            capture.__channelBuffers = [];
            capture.__sampleCount = 0;
            for (var i = 0; i < capture.numChannels; i++) {
                capture.__channelBuffers.push([]);
            }
        },



        __success:  function(stream) {
            capture.__recordingStream = stream;
            // creates the audio context
            var audioContext = window.AudioContext || window.webkitAudioContext;
            var context = new audioContext();

            // Acquire the sample rate
            capture.sampleRate = context.sampleRate;

            // Create a gain node
            var volume = context.createGain();

            // Create a source node that will get data from the microphone
            var audioInput = context.createMediaStreamSource(capture.__recordingStream);
            // Send to volume node
            audioInput.connect(volume);

            // From the spec: This value controls how frequently the audioprocess event is
            // dispatched and how many sample-frames need to be processed each call.
            // Lower values for buffer size will result in a lower (better) latency.
            // Higher values will be necessary to avoid audio breakup and glitches
            // Two input channels
            //
            var bufferSize = 2048;
            var recorder = context.createJavaScriptNode(bufferSize, capture.numChannels, capture.numChannels);

            recorder.onaudioprocess = function(e){
                if (capture.recording) {
                    for (var i = 0; i < capture.numChannels; i++) {
                        var samples = e.inputBuffer.getChannelData(i);
                        // Clone the samples
                        capture.__channelBuffers[i].push(new Float32Array(samples));
                    }
                    capture.__sampleCount += bufferSize;
                }
            };

            // we connect the recorder
            volume.connect (recorder);
            recorder.connect (context.destination);

            capture.gotCapture = true;
            capture.__gotCaptureFn(capture);
        },

        __failure: function(e) {
            capture.__deniedFn(capture);
        },


        acquireCapture: function() {
            capture.__initChannelBuffers();

            if (navigator.getUserMedia) {
                navigator.getUserMedia({video: false, audio: true}, capture.__success, capture.__failure);
            }
            else if (navigator.webkitGetUserMedia) {
                navigator.webkitGetUserMedia({video: false, audio: true}, capture.__success, capture.__failure);
            }
            else if (navigator.mozGetUserMedia) {
                navigator.mozGetUserMedia({video: false, audio: true}, capture.__success, capture.__failure);
            }
            else if (navigator.msGetUserMedia) {
                navigator.msGetUserMedia({video: false, audio: true}, capture.__success, capture.__failure);
            }
        },

        startRecording: function() {
            if (capture.__recordingStream !== null) {
                capture.recording = true;
                capture.__startFn(capture);
            }
        },

        stopRecording: function() {
            if (capture.__recordingStream !== null) {
                capture.recording = false;
            }

            // Merge the buffers
            var merged = [];
            for (var i = 0; i < capture.numChannels; i++) {
                merged.push(larch.media.__mergeAudioBuffers(capture.__channelBuffers[i], capture.__sampleCount));
            }

            // Interleave channels
            var interleaved;
            if (capture.numChannels === 1) {
                interleaved = merged[0];
            }
            else if (capture.numChannels === 2) {
                interleaved = larch.media.__interleaveAudioChannels(merged[0], merged[1]);
            }
            else {
                throw 'Unsupported value for capture.numChannels'
            }

            var blob = null, buffer = null, view = null, numInterleavedSamples = interleaved.length, index = 0;
            if (capture.__format == 'rawf32') {
                buffer = new ArrayBuffer(interleaved.length * 4);
                view = new DataView(buffer);

                index = 0;
                for (var i = 0; i < numInterleavedSamples; i++){
                    view.setFloat32(index, interleaved[i], true);
                    index += 4;
                }

                // our final binary blob that we can hand off
                blob = new Blob ( [ view ], { type : 'application/octet-stream' } );
            }
            else if (capture.__format == 'raw16') {
                buffer = new ArrayBuffer(interleaved.length * 2);
                view = new DataView(buffer);

                index = 0;
                for (var i = 0; i < numInterleavedSamples; i++){
                    view.setInt16(index, interleaved[i] * 0x7fff, true);
                    index += 2;
                }

                // our final binary blob that we can hand off
                blob = new Blob ( [ view ], { type : 'application/octet-stream' } );
            }
            else if (capture.__format == 'raw8') {
                buffer = new ArrayBuffer(interleaved.length);
                view = new DataView(buffer);

                index = 0;
                for (var i = 0; i < numInterleavedSamples; i++){
                    view.setInt8(index, interleaved[i] * 0x7f, true);
                    index++;
                }

                // our final binary blob that we can hand off
                blob = new Blob ( [ view ], { type : 'application/octet-stream' } );
            }
            else if (capture.__format == 'wav') {
                // create the buffer and view to create the .WAV file
                buffer = new ArrayBuffer(44 + interleaved.length * 2);
                view = new DataView(buffer);

                // write the WAV container, check spec at: https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
                // RIFF chunk descriptor
                larch.media.__writeStringToMemoryView(view, 0, 'RIFF');                             // ChunkID
                view.setUint32(4, 44 + interleaved.length * 2, true);       // ChunkSize
                larch.media.__writeStringToMemoryView(view, 8, 'WAVE');                 // Format
                // FMT sub-chunk
                larch.media.__writeStringToMemoryView(view, 12, 'fmt ');        //Subchunk1ID
                view.setUint32(16, 16, true);           //Subchunk1Size - 16 bytes
                view.setUint16(20, 1, true);        //AudioFormat: 1 = PCM
                view.setUint16(22, capture.numChannels, true);      //NumChannels
                view.setUint32(24, capture.sampleRate, true);            //SampleRate
                view.setUint32(28, capture.sampleRate * capture.numChannels * 2, true);       // ByteRate = SampleRate * NumChannels * BytesPerSample
                view.setUint16(32, capture.numChannels * 2, true);       // BlockAlign = NumChannels * BytesPerSample
                view.setUint16(34, 16, true);       // BitsPerSample
                // data sub-chunk
                larch.media.__writeStringToMemoryView(view, 36, 'data');        //Subchunk2ID
                view.setUint32(40, interleaved.length * 2, true);       //Subchunk2Size

                // write the PCM samples
                index = 44;
                for (var i = 0; i < numInterleavedSamples; i++){
                    view.setInt16(index, interleaved[i] * 0x7FFF, true);
                    index += 2;
                }

                // our final binary blob that we can hand off
                blob = new Blob ( [ view ], { type : 'audio/wav' } );
            }

            // Put the value in __sampleCount into numSamples
            capture.numSamples = capture.__sampleCount;

            capture.__audioDataFn(capture, blob);

            capture.__initChannelBuffers();
        }
    };

    return capture;
};



larch.media.initAudioCaptureButton = function(node, numChannels, format) {
    var capture = larch.media.audioCapture(numChannels, format,
        // Got capture callback
        function(capture) {
            button.button('option', 'label', 'Record');
            button.button('option', 'icons', {primary: 'ui-icon-play', secondary: ''});
            button.button('refresh');
        },
        // Denied access callback
        function(capture) {
            noty({text: 'User denied access to microphone', type:'alert', timeout: 2000, layout:'bottomCenter'});
            button.button('option', 'label', 'Denied');
            button.button('option', 'icons', {primary: 'ui-icon-alert', secondary: ''});
            button.button('option', 'disabled', true);
            button.button('refresh');
        },
        // Started recording callback
        function(capture) {
            noty({text: 'Recording', type:'warning', timeout: 2000, layout:'bottomCenter'});
            button.button('option', 'label', 'Stop');
            button.button('option', 'icons', {primary: 'ui-icon-stop', secondary: ''});
            button.button('refresh');
        },
        // Audio data callback
        function(catpure, audioData) {
            var segment_id = larch.__getSegmentIDForEvent(node);
            var fd = new FormData();
            fd.append('__larch_segment_id', segment_id);
            fd.append('num_channels', '' + capture.numChannels);
            fd.append('sample_rate', '' + capture.sampleRate);
            fd.append('num_samples', '' + capture.numSamples);
            fd.append('data', audioData);
            $.ajax({
                data: fd,
                url: '/form/' + larch.__doc_url + '/' + larch.__view_id,
                dataType: 'json',
                type: 'POST',
                processData: false,
                contentType: false,
                success: function(msg) {
                    larch.__handleMessagesFromServer(msg);
                }
            });

            noty({text: 'Stopped', type:'success', timeout: 2000, layout:'bottomCenter'});
        }
    );

    var q = $(node);
    var button = q.button({label: 'Get mic', icons: {primary: 'ui-icon-unlocked', secondary: ''}});
    button.click(function(ui, event) {
        if (!larch.media.hasGetUserMedia()) {
            noty({text: 'user media API unavailable', type:'error', timeout: 2000, layout:'bottomCenter'});
        }
        if (!capture.gotCapture) {
            capture.acquireCapture();
        }
        else {
            if (capture.recording) {
                capture.stopRecording();
                button.button('option', 'label', 'Record');
                button.button('option', 'icons', {primary: 'ui-icon-play', secondary: ''});
                button.button('refresh');
            }
            else {
                capture.startRecording();
            }
        }
    });
};