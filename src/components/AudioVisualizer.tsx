import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { GUI } from 'dat.gui';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass';

interface AudioVisualizerProps {
  stream: MediaStream | null;
  isActive: boolean;
}

const vertexShader = `
  uniform float u_time;
  // ... (paste the entire vertex shader code from your index.html here)
`;

const fragmentShader = `
  uniform float u_red;
  uniform float u_green;
  uniform float u_blue;
  void main() {
      gl_FragColor = vec4(vec3(u_red, u_green, u_blue), 1.);
  }
`;

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ stream, isActive }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    if (!containerRef.current) return;

    // Three.js setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(300, 300); // Smaller size for the mic button
    containerRef.current.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);

    const params = {
      red: 1.0,
      green: 1.0,
      blue: 1.0,
      threshold: 0.5,
      strength: 0.5,
      radius: 0.8
    };

    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const renderScene = new RenderPass(scene, camera);
    const bloomPass = new UnrealBloomPass(new THREE.Vector2(300, 300));
    bloomPass.threshold = params.threshold;
    bloomPass.strength = params.strength;
    bloomPass.radius = params.radius;

    const bloomComposer = new EffectComposer(renderer);
    bloomComposer.addPass(renderScene);
    bloomComposer.addPass(bloomPass);
    bloomComposer.addPass(new OutputPass());

    camera.position.set(0, 0, 10);
    camera.lookAt(0, 0, 0);

    const uniforms = {
      u_time: { type: 'f', value: 0.0 },
      u_frequency: { type: 'f', value: 0.0 },
      u_red: { type: 'f', value: 1.0 },
      u_green: { type: 'f', value: 1.0 },
      u_blue: { type: 'f', value: 1.0 }
    };

    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader,
      fragmentShader
    });

    const geometry = new THREE.IcosahedronGeometry(4, 20);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    mesh.material.wireframe = true;

    // Audio setup
    if (stream) {
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 32;
      source.connect(analyser);
      analyserRef.current = analyser;
    }

    const clock = new THREE.Clock();

    const animate = () => {
      if (!isActive) return;

      uniforms.u_time.value = clock.getElapsedTime();

      if (analyserRef.current) {
        const frequencyData = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(frequencyData);
        const average = frequencyData.reduce((a, b) => a + b) / frequencyData.length;
        uniforms.u_frequency.value = average;
      }

      mesh.rotation.x += 0.01;
      mesh.rotation.y += 0.01;

      bloomComposer.render();
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      renderer.dispose();
      geometry.dispose();
      material.dispose();
    };
  }, [stream, isActive]);

  return <div ref={containerRef} className="w-12 h-12 rounded-full overflow-hidden" />;
}; 