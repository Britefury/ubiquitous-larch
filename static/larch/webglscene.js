//-*************************
//-* This program is free software; you can use it, redistribute it and/or
//-* modify it under the terms of the GNU Affero General Public License
//-* version 3 as published by the Free Software Foundation. The full text of
//-* the GNU Affero General Public License version 3 can be found in the file
//-* named 'LICENSE.txt' that accompanies this program. This source code is
//-* (C)copyright Geoffrey French 2011-2014.
//-*************************

function webglscene(canvas) {
    var glc = {};



    glc.degToRad = function(deg) {
        return deg * (Math.PI / 180.0);
    };


    glc.canvas = canvas;
    glc.gl = null;
    glc.camera = null;
    glc.entities = [];

    try {
        glc.gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    }
    catch (e) {
        console.log("Caught " + e + " when initialising webgl");
    }

    var __textureUnits = [glc.gl.TEXTURE0, glc.gl.TEXTURE1, glc.gl.TEXTURE2, glc.gl.TEXTURE3, glc.gl.TEXTURE4, glc.gl.TEXTURE5, glc.gl.TEXTURE6, glc.gl.TEXTURE7];


    // SET CAMERA
    glc.setCamera = function(camera) {
        glc.camera = camera;
    };


    // ADD ENTITY
    glc.addEntity = function(entity) {
        glc.entities.push(entity);
        glc.queueRedraw();
    };



    // REDRAW

    glc.redraw = function () {
        var gl = glc.gl;
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.enable(gl.DEPTH_TEST);
        gl.depthFunc(gl.LEQUAL);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);


        for (var i = 0; i < glc.entities.length; i++) {
            var entity = glc.entities[i];
            entity.draw();
        }
    };


    glc.__redrawQueued = false;

    glc.queueRedraw = function() {
        if (!glc.__redrawQueued) {
            glc.__redrawQueued = true;
            setTimeout(function() {
                glc.__redrawQueued = false;
                glc.redraw();
            }, 0);
        }
    };



    // SHADER CREATION
    glc.createShader = function(vsSources, fsSources) {
        var gl = glc.gl;
        var i;
        var shader = {
            vsSources: vsSources,
            fsSources: fsSources
        };
        //
        // SHADERS
        //

        var vertexShaders = [];
        for (i = 0; i < vsSources.length; i++) {
            var vertexShader = gl.createShader(gl.VERTEX_SHADER);
            gl.shaderSource(vertexShader, vsSources[i]);
            gl.compileShader(vertexShader);

            if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
                alert("Vertex shader compile failed " + gl.getShaderInfoLog(vertexShader));
            }

            vertexShaders.push(vertexShader);
        }


        var fragmentShaders = [];
        for (i = 0; i < fsSources.length; i++) {
            var fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
            gl.shaderSource(fragmentShader, fsSources[i]);
            gl.compileShader(fragmentShader);

            if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
                alert("Fragment shader compile failed " + gl.getShaderInfoLog(fragmentShader));
            }

            fragmentShaders.push(fragmentShader);
        }


        // Create the program
        var shaderProgram = gl.createProgram();
        // Attach the vertex shaders
        for (i = 0; i < vertexShaders.length; i++) {
            gl.attachShader(shaderProgram, vertexShaders[i]);
        }
        // Attach the fragment shaders
        for (i = 0; i < fragmentShaders.length; i++) {
            gl.attachShader(shaderProgram, fragmentShaders[i]);
        }
        // Link
        gl.linkProgram(shaderProgram);

        if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
            alert("Unable to link the shader program." + gl.getProgramInfoLog(shaderProgram));
        }

        shader.shaderProgram = shaderProgram;


        shader.use = function() {
            gl.useProgram(shader.shaderProgram);
        };

        shader.useForRendering = function() {
            shader.use();
            if (glc.camera !== null) {
                glc.camera.apply(shader);
            }
        };

        shader.getUniformLocation = function(name) {
            return gl.getUniformLocation(shader.shaderProgram, name);
        };

        shader.getAttribLocation = function(name) {
            return gl.getAttribLocation(shader.shaderProgram, name);
        };

        return shader;
    };


    glc.createTexture = function() {
        var texture = {};

        var gl = glc.gl;

        if (gl) {
            texture.texId = gl.createTexture();
        }

        texture.attach = function(shader, texNum, samplerName) {
            throw "Abstract";
        };

        return texture;
    };


    glc.createTexture2D = function(rsc) {
        var texture = glc.createTexture();

        var gl = glc.gl;

        if (gl) {
            var img = new Image();
            img.onload = function() {
                gl.bindTexture(gl.TEXTURE_2D, texture.texId);
                gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_NEAREST);
                gl.generateMipmap(gl.TEXTURE_2D);
                gl.bindTexture(gl.TEXTURE_2D, null);
            };
            img.src = rsc.url;

            texture.image = img;

            texture.attach = function(shader, texNum, samplerName) {
                gl.activeTexture(__textureUnits[texNum]);
                gl.bindTexture(gl.TEXTURE_2D, texture.texId);
                gl.uniform1i(shader.getUniformLocation(samplerName), texNum);
            };
        }

        return texture;
    };


    glc.createTextureCube = function(resources) {
        var texture = glc.createTexture();

        var gl = glc.gl;

        if (gl) {
            var imgs = [];
            var count = [0];

            var onloadtex = function() {
                count[0]++;
                if (count[0] == 6) {
                    gl.bindTexture(gl.TEXTURE_CUBE_MAP, texture.texId);
                    gl.texParameteri(gl.TEXTURE_CUBE_MAP, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
                    gl.texParameteri(gl.TEXTURE_CUBE_MAP, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_NEAREST);
                    //gl.texParameteri(gl.TEXTURE_CUBE_MAP, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
                    //gl.texParameteri(gl.TEXTURE_CUBE_MAP, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
                    //gl.texParameteri(gl.TEXTURE_CUBE_MAP, gl.TEXTURE_WRAP_R, gl.CLAMP_TO_EDGE);

                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_NEGATIVE_X, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[0]);
                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_POSITIVE_X, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[1]);
                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_NEGATIVE_Y, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[2]);
                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_POSITIVE_Y, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[3]);
                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_NEGATIVE_Z, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[4]);
                    gl.texImage2D(gl.TEXTURE_CUBE_MAP_POSITIVE_Z, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, imgs[5]);
                    gl.generateMipmap(gl.TEXTURE_CUBE_MAP);

                    gl.generateMipmap(gl.TEXTURE_CUBE_MAP);
                    gl.bindTexture(gl.TEXTURE_CUBE_MAP, null);
                }
            };

            for (var i = 0; i < resources.length; i++) {
                var img = new Image();
                img.src = resources[i].url;
                img.onload = onloadtex;
                imgs.push(img);
            }

            texture.images = imgs;

            texture.attach = function(shader, texNum, samplerName) {
                gl.activeTexture(__textureUnits[texNum]);
                gl.bindTexture(gl.TEXTURE_CUBE_MAP, texture.texId);
                gl.uniform1i(shader.getUniformLocation(samplerName), texNum);
            };
        }

        return texture;
    };


    glc.createMaterial = function(shader, samplerNamesToTextures, useBlending) {
        var material = {
            shader: shader,
            useBlending: useBlending
        };


        var samplerNamesAndTextures = [];
        for (var samplerName in samplerNamesToTextures) {
            if (samplerNamesToTextures.hasOwnProperty(samplerName)) {
                var texture = samplerNamesToTextures[samplerName];
                var sAndT = [samplerName, texture];
                samplerNamesAndTextures.push(sAndT);
            }
        }

        material.samplerNamesAndTextures = samplerNamesAndTextures;


        material.useForRendering = function() {
            var gl = glc.gl;

            material.shader.useForRendering();
            for (var i = 0; i < material.samplerNamesAndTextures.length; i++) {
                var sAndT = material.samplerNamesAndTextures[i];
                sAndT[1].attach(material.shader, i, sAndT[0]);
            }
            if (material.useBlending) {
                gl.blendFunc(gl.ONE, gl.SRC_ALPHA);
                gl.enable(gl.BLEND);
            }
            else {
                gl.disable(gl.BLEND);
            }
        };

        return material;
    };



    glc.createTurntableCamera = function(fovY, nearFrac, farFrac, focalPoint, orbitalRadius, azimuth, altitude) {
        var camera = {};
        camera.fovY = fovY;
        camera.aspectRatio = glc.canvas.width / glc.canvas.height;
        camera.nearFrac = nearFrac;
        camera.farFrac = farFrac;
        camera.focalPoint = focalPoint;
        camera.orbitalRadius = orbitalRadius;
        camera.azimuth = azimuth;
        camera.altitude = altitude;
        camera._navFunction = null;
        camera._navPos = null;

        glc.canvas.onmousedown = function (evt) {
            if (evt.altKey) {
                camera._navFunction = evt.button;
                camera._navPos = [evt.offsetX, evt.offsetY];
                return false;
            }
            else {
                return true;
            }
        };

        glc.canvas.onmouseup = function (evt) {
            camera._navFunction = null;
        };

        glc.canvas.onmousemove = function (evt) {
            if (camera._navFunction !== null) {
                var dx = evt.offsetX - camera._navPos[0];
                var dy = camera._navPos[1] - evt.offsetY;

                if (camera._navFunction === 0) {
                    camera.rotate(-dx * 0.01, -dy * 0.01);
                    glc.redraw();
                }
                else if (camera._navFunction === 1) {
                }
                else if (camera._navFunction === 2) {
                    camera.zoom(Math.pow(Math.pow(2.0, 0.005), -dx));
                    glc.redraw();
                }
                camera._navPos = [evt.offsetX, evt.offsetY];
            }
        };

        camera.apply = function (shader) {
            var gl = glc.gl;
            var near = camera.nearFrac * camera.orbitalRadius;
            var far = camera.farFrac * camera.orbitalRadius;

            var projectionMatrix = mat4.create();
            mat4.perspective(projectionMatrix, fovY, camera.aspectRatio, near, far);

            // Camera matrix
            var cameraMatrix = camera._createWorldToCameraMatrix();
            //cameraMatrix = mat4.create();
            //mat4.lookAt(cameraMatrix, [0.0, 6.0*Math.sin(glc.degToRad(30.0)), -6.0*Math.cos(glc.degToRad(30.0))], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]);

            var pUniform = shader.getUniformLocation("projectionMatrix");
            gl.uniformMatrix4fv(pUniform, false, new Float32Array(projectionMatrix));

            var mvUniform = shader.getUniformLocation("cameraMatrix");
            gl.uniformMatrix4fv(mvUniform, false, new Float32Array(cameraMatrix));


            var camPosUniform = shader.getUniformLocation("camPos");
            if (camPosUniform != -1) {
                var invMV = mat4.create();
                mat4.invert(invMV, cameraMatrix);
                var origin = vec4.fromValues(0, 0, 0, 1);
                var camPos = vec4.create();
                vec4.transformMat4(camPos, origin, invMV);
                gl.uniform4fv(camPosUniform, new Float32Array(camPos));
            }
        };

        camera._createWorldToCameraMatrix = function () {
            var cameraMatrix = mat4.create();
            var invPos = vec3.create();
            vec3.negate(invPos, camera.focalPoint);

            // Move the world and camera so that the camera lies at the origin
            mat4.translate(cameraMatrix, cameraMatrix, [0.0, 0.0, -camera.orbitalRadius]);

            // Rotate the world and camera so that the camera rests on the XZ plane
            mat4.rotateX(cameraMatrix, cameraMatrix, camera.altitude);

            // Rotate the world so that the camera lies on the forward axis
            mat4.rotateY(cameraMatrix, cameraMatrix, -camera.azimuth);

            // Move the focal point to the centre of the world
            mat4.translate(cameraMatrix, cameraMatrix, invPos);

            return cameraMatrix;
        };

        camera._createCameraToWorldRotationMatrix = function () {
            // Inverse of _createWorldToCameraMatrix(), but rotations only
            var cameraMatrix = mat3.create();

            mat3.rotateY(cameraMatrix, cameraMatrix, camera.azimuth);
            mat3.rotateX(cameraMatrix, cameraMatrix, -camera.altitude);

            return cameraMatrix;
        };


        camera.translate = function (translation) {
            vec3.add(camera.focalPoint, camera.focalPoint, translation);
        };

        camera.zoom = function (zoomFactor) {
            camera.orbitalRadius *= zoomFactor;
        };

        camera.rotate = function (azimuth, altitude) {
            camera.azimuth = (this.azimuth + azimuth) % (Math.PI*2);
            camera.altitude += altitude;
            camera.altitude = Math.min(Math.max(camera.altitude, -Math.PI * 0.5), Math.PI * 0.5);
        };

        camera.pan = function (translationInCameraSpace) {
            var camRot = camera._createCameraToWorldRotationMatrix();
            var translationInWorldSpace = vec3.create();
            vec3.transformMat3(translationInWorldSpace, translationInCameraSpace, camRot);

            camera.translate(translationInWorldSpace);
        };

        return camera;
    };



    glc.createEntity = function() {
        var entity = {
        };

        entity.draw = function() {
            throw 'Abstract';
        };

        return entity;
    };



    glc.createLiteralMeshEntity = function(material, vertexAttribNamesSizes, vertices, indexBufferModesData) {
        var entity = glc.createEntity();
        entity.material = material;

        var gl = glc.gl;

        //
        // CREATE VERTICES BUFFER
        //

        var verticesBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, verticesBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
        entity.verticesBuffer = verticesBuffer;


        //
        // GET ATTRIBUTE LOCATIONS
        //

        var attribLocations = [];
        var attribSizes = [];
        var attribStride = 0;
        for (var i = 0; i < vertexAttribNamesSizes.length; i++) {
            var loc = material.shader.getAttribLocation(vertexAttribNamesSizes[i][0]);
            gl.enableVertexAttribArray(loc);

            attribLocations.push(loc);
            var sz = vertexAttribNamesSizes[i][1];
            attribSizes.push(sz);
            attribStride += sz;
        }
        entity.attribLocations = attribLocations;
        entity.attribSizes = attribSizes;
        entity.attribStride = attribStride;


        //
        // CREATE INDICES BUFFER
        //

        var indexBuffers = [];
        var indexBufferModes = [];
        var indexBufferSizes = [];

        var _modeNameToMode = {
            points: gl.POINTS,
            line_strip: gl.LINE_STRIP,
            line_loop: gl.LINE_LOOP,
            lines: gl.LINES,
            triangle_strip: gl.TRIANGLE_STRIP,
            triangle_fan: gl.TRIANGLE_FAN,
            triangles: gl.TRIANGLES
        };

        for (var i = 0; i < indexBufferModesData.length; i++) {
            var mode = _modeNameToMode[indexBufferModesData[i][0]];
            var indices = indexBufferModesData[i][1];
            var indicesBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indicesBuffer);
            gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.STATIC_DRAW);
            indexBuffers.push(indicesBuffer);
            indexBufferModes.push(mode);
            indexBufferSizes.push(indices.length);
        }
        entity.indexBuffers = indexBuffers;
        entity.indexBufferModes = indexBufferModes;
        entity.indexBufferSizes = indexBufferSizes;


        entity.draw = function() {
            entity.material.useForRendering();
            //
            // OBJECT
            //

            gl.bindBuffer(gl.ARRAY_BUFFER, entity.verticesBuffer);
            var offset = 0;
            for (var i = 0; i < entity.attribLocations.length; i++) {
                gl.vertexAttribPointer(entity.attribLocations[i], entity.attribSizes[i], gl.FLOAT, false, entity.attribStride * 4, offset * 4);
                offset += entity.attribSizes[i];
            }

            for (var i = 0; i < entity.indexBuffers.length; i++) {
                gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, entity.indexBuffers[i]);
                gl.drawElements(entity.indexBufferModes[i], entity.indexBufferSizes[i], gl.UNSIGNED_SHORT, 0);
            }
        };

        return entity;
    };


    glc.createUVMeshEntity = function(material) {
        var entity = glc.createEntity();
        entity.material = material;

        var gl = glc.gl;

        entity.verticesBuffer = gl.createBuffer();
        entity.indexBuffer = gl.createBuffer();

        entity.__ready = false;


        entity.refreshUVMesh = function(uSegs, vSegs, closedU, closedV, vertexPositions, vertexAttribsNamesSizesData) {
            //
            // Convert incoming arrays to Float32Arrays
            // Compute total vertex size
            //
            vertexPositions = new Float32Array(vertexPositions);
            var vertexSize = 6;		// Account for position and normal
            for (var i = 0; i < vertexAttribsNamesSizesData.length; i++) {
                vertexSize += vertexAttribsNamesSizesData[i][1];
                vertexAttribsNamesSizesData[i][2] = new Float32Array(vertexAttribsNamesSizesData[i][2]);
            }


            //
            // ASSEMBLE VERTEX ARRAY
            //

            var bufferSize = vertexSize * uSegs * vSegs;
            var vertices = new Float32Array(bufferSize);

            for (var y = 0; y < vSegs; y++) {
                for (var x = 0; x < uSegs; x++) {
                    // Vertex position
                    var ndx = x + y * uSegs;
                    var pos = [vertexPositions[ndx * 3], vertexPositions[ndx * 3 + 1], vertexPositions[ndx * 3 + 2]];

                    // Get adjacent vertices and compute normal
                    var ixp = x > 0 ? x - 1 : (closedU ? uSegs - 1 : 0);			// X-prev
                    var ixn = x < uSegs - 1 ? x + 1 : (closedU ? 0 : uSegs - 1);	// X-next
                    var iyp = y > 0 ? y - 1 : (closedV ? vSegs - 1 : 0);			// Y-prev
                    var iyn = y < vSegs - 1 ? y + 1 : (closedV ? 0 : vSegs - 1);	// Y-next
                    var vxp = [vertexPositions[(ixp + y * uSegs) * 3], vertexPositions[(ixp + y * uSegs) * 3 + 1], vertexPositions[(ixp + y * uSegs) * 3 + 2]];
                    var vxn = [vertexPositions[(ixn + y * uSegs) * 3], vertexPositions[(ixn + y * uSegs) * 3 + 1], vertexPositions[(ixn + y * uSegs) * 3 + 2]];
                    var vyp = [vertexPositions[(x + iyp * uSegs) * 3], vertexPositions[(x + iyp * uSegs) * 3 + 1], vertexPositions[(x + iyp * uSegs) * 3 + 2]];
                    var vyn = [vertexPositions[(x + iyn * uSegs) * 3], vertexPositions[(x + iyn * uSegs) * 3 + 1], vertexPositions[(x + iyn * uSegs) * 3 + 2]];
                    var u = [vxn[0] - vxp[0], vxn[1] - vxp[1], vxn[2] - vxp[2]];
                    var v = [vyn[0] - vyp[0], vyn[1] - vyp[1], vyn[2] - vyp[2]];
                    var n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
                    var nlen = Math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
                    var invl = nlen == 0.0 ? 1.0 : 1.0 / nlen;
                    n = [n[0] * -invl, n[1] * -invl, n[2] * -invl];

                    // Add to array
                    var offset = ndx * vertexSize;
                    vertices[offset] = pos[0];
                    vertices[offset + 1] = pos[1];
                    vertices[offset + 2] = pos[2];
                    vertices[offset + 3] = n[0];
                    vertices[offset + 4] = n[1];
                    vertices[offset + 5] = n[2];

                    offset += 6;
                    // Deal with remaining attributes
                    for (var i = 0; i < vertexAttribsNamesSizesData.length; i++) {
                        var sz = vertexAttribsNamesSizesData[i][1];
                        for (var j = 0; j < sz; j++) {
                            vertices[offset + j] = vertexAttribsNamesSizesData[i][2][ndx * sz + j];
                        }
                        offset += sz;
                    }
                }
            }


            //
            // CREATE VERTICES BUFFER
            //

            gl.bindBuffer(gl.ARRAY_BUFFER, entity.verticesBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);


            //
            // GET ATTRIBUTE LOCATIONS
            //

            var attribLocations = [];
            var attribSizes = [];

            // Handle position and normal first

            var vertexPosLoc = entity.material.shader.getAttribLocation("vertexPos");
            gl.enableVertexAttribArray(vertexPosLoc);
            attribLocations.push(vertexPosLoc);
            attribSizes.push(3);

            var vertexNrmLoc = entity.material.shader.getAttribLocation("vertexNrm");
            gl.enableVertexAttribArray(vertexNrmLoc);
            attribLocations.push(vertexNrmLoc);
            attribSizes.push(3);

            var attribStride = 6;

            // Now handle remaining attributes

            for (var i = 0; i < vertexAttribsNamesSizesData.length; i++) {
                var loc = entity.material.shader.getAttribLocation(vertexAttribsNamesSizesData[i][0]);
                gl.enableVertexAttribArray(loc);

                attribLocations.push(loc);
                var sz = vertexAttribsNamesSizesData[i][1];
                attribSizes.push(sz);
                attribStride += sz;
            }
            entity.attribLocations = attribLocations;
            entity.attribSizes = attribSizes;
            entity.attribStride = attribStride;


            //
            // CREATE INDICES BUFFER
            //

            var numRows = closedV ? vSegs : vSegs - 1;
            var numColumns = closedU ? uSegs : uSegs - 1;
            var indices = new Uint16Array(numRows * numColumns * 6);

            var ndx = 0;
            for (var y = 0; y < (vSegs - 1); y++) {
                for (var x = 0; x < (uSegs - 1); x++) {
                    var a = y * uSegs + x;
                    var b = a + 1;
                    var c = a + uSegs;
                    var d = c + 1;
                    indices[ndx] = a;
                    indices[ndx + 1] = b;
                    indices[ndx + 2] = c;
                    indices[ndx + 3] = b;
                    indices[ndx + 4] = d;
                    indices[ndx + 5] = c;
                    ndx += 6;
                }
                if (closedU) {
                    var a = y * uSegs + uSegs - 1;
                    var b = y * uSegs;
                    var c = a + uSegs;
                    var d = b + uSegs;
                    indices[ndx] = a;
                    indices[ndx + 1] = b;
                    indices[ndx + 2] = c;
                    indices[ndx + 3] = b;
                    indices[ndx + 4] = d;
                    indices[ndx + 5] = c;
                    ndx += 6;
                }
            }
            if (closedV) {
                for (var x = 0; x < (uSegs - 1); x++) {
                    var a = (vSegs - 1) * uSegs + x;
                    var b = a + 1;
                    var c = x;
                    var d = c + 1;
                    indices[ndx] = a;
                    indices[ndx + 1] = b;
                    indices[ndx + 2] = c;
                    indices[ndx + 3] = b;
                    indices[ndx + 4] = d;
                    indices[ndx + 5] = c;
                    ndx += 6;
                }
                if (closedU) {
                    var a = (vSegs - 1) * uSegs + uSegs - 1;
                    var b = (vSegs - 1) * uSegs;
                    var c = uSegs - 1;
                    var d = 0;
                    indices[ndx] = a;
                    indices[ndx + 1] = b;
                    indices[ndx + 2] = c;
                    indices[ndx + 3] = b;
                    indices[ndx + 4] = d;
                    indices[ndx + 5] = c;
                    ndx += 6;
                }
            }


            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, entity.indexBuffer);
            gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
            entity.numElements = indices.length;

            entity.__ready = true;

            return entity;
        };


        entity.draw = function() {
            var gl = glc.gl;

            if (entity.__ready) {
                entity.material.useForRendering();

                //
                // OBJECT
                //

                gl.bindBuffer(gl.ARRAY_BUFFER, entity.verticesBuffer);
                var offset = 0;
                for (var i = 0; i < entity.attribLocations.length; i++) {
                    gl.vertexAttribPointer(entity.attribLocations[i], entity.attribSizes[i], gl.FLOAT, false, entity.attribStride * 4, offset * 4);
                    offset += entity.attribSizes[i];
                }

                gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, entity.indexBuffer);
                gl.drawElements(gl.TRIANGLES, entity.numElements, gl.UNSIGNED_SHORT, 0);
            }
        };



        entity.attachResource = function(resource) {
            var update = function() {
                resource.fetchJSON(function (data) {
                    entity.refreshUVMesh(data.uSegs, data.vSegs, data.closedU, data.closedV, data.vertexPositions, data.vertexAttribsNamesSizesData);
                    glc.queueRedraw();
                });
            };

            resource.addListener(update);
            update();

            return entity;
        };


        return entity;
    };



    glc.createSkybox = function(materials) {
        var entity = glc.createEntity();

        var verts = [
            [ -5.0, -5.0, -5.0 ],
            [ 5.0, -5.0, -5.0 ],
            [ -5.0, 5.0, -5.0 ],
            [ 5.0, 5.0, -5.0 ],
            [ -5.0, -5.0, 5.0 ],
            [ 5.0, -5.0, 5.0 ],
            [ -5.0, 5.0, 5.0 ],
            [ 5.0, 5.0, 5.0 ]
        ];
        var vert_indices = [
            [4, 0, 2, 6],		// X-neg  --+  ---  -+-  -++
            [1, 5, 7, 3],		// X-pos  +--  +-+  +++  ++-
            [4, 5, 1, 0],		// Y-neg  --+  +-+  +--  ---
            [2, 3, 7, 6],		// Y-pos  -+-  ++-  +++  -++
            [0, 1, 3, 2],		// Z-neg  ---  +--  ++-  -+-
            [5, 4, 6, 7]			// Z-pos  +-+  --+  -++  +++
        ];

        var tex_coords = [
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 0.0]
        ];


        var faces = [];

        for (var faceIndex = 0; faceIndex < 6; faceIndex++) {
            var faceVerts = [];

            var idxs = vert_indices[faceIndex];
            for (var faceVertIndex = 0; faceVertIndex < 4; faceVertIndex++) {
                faceVerts.push(verts[idxs[faceVertIndex]][0]);
                faceVerts.push(verts[idxs[faceVertIndex]][1]);
                faceVerts.push(verts[idxs[faceVertIndex]][2]);
                faceVerts.push(tex_coords[faceVertIndex][0]);
                faceVerts.push(tex_coords[faceVertIndex][1]);
            }

            var face =  glc.createLiteralMeshEntity(materials[faceIndex], [['vertexPos', 3], ['vertexTex', 2]], faceVerts, [['triangles', [0, 1, 2, 0, 2, 3]]]);
            faces.push(face);
        }

        entity.faces = faces;

        entity.draw = function() {
            var gl = glc.gl;

            gl.disable(gl.DEPTH_TEST);
            gl.depthMask(false);

            for (var i = 0; i < entity.faces.length; i++) {
                entity.faces[i].draw();
            }

            gl.enable(gl.DEPTH_TEST);
            gl.depthMask(true);
        };

        return entity;
    };


    return glc;
}

