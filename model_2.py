
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import html
import json

st.set_page_config(
    page_title="AI Wind Tunnel",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# AI MODEL
# =========================================================

def predict_downforce(speed_kmh, wing_angle_deg):
    """
    Replace the demo formula with your trained model.

    Example:
        import joblib
        model = joblib.load("downforce_model.pkl")
        return float(model.predict([[speed_kmh, wing_angle_deg]])[0])
    """
    # Demo only: NOT a validated aerodynamic prediction.
    v = speed_kmh / 3.6
    return float(
        0.5 * 1.225 * v**2 * 1.5
        * max(0, np.sin(np.radians(wing_angle_deg))) * 1.8
    )


# =========================================================
# STREAMLIT CONTROLS
# =========================================================

st.markdown("""
<style>
.stApp {
    background: #07111d;
    color: #eaf5ff;
}
section[data-testid="stSidebar"] {
    background: #091725;
    border-right: 1px solid #24415a;
}
h1, h2, h3, p, label { color: #eaf5ff; }
div[data-testid="stMetric"] {
    background: #0d2031;
    border: 1px solid #23445d;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌬️ AI WIND TUNNEL")
st.caption("AERODYNAMIC DOWNFORCE SIMULATOR  /  REAL-TIME 3D")

with st.sidebar:
    st.markdown("## Simulation controls")
    speed = st.slider("Vehicle speed (km/h)", 50, 300, 180)
    wing_angle = st.slider("Rear wing angle (°)", 0, 25, 12)

    st.markdown("## Visualization")
    show_streamlines = st.toggle("Show streamlines", True)
    show_particles = st.toggle("Show particles", True)
    show_tunnel = st.toggle("Show tunnel", True)
    show_car = st.toggle("Show car", True)

    camera = st.selectbox(
        "Camera",
        ["Three-quarter", "Side", "Front", "Top", "Rear"],
    )

    st.caption("Drag to orbit · Scroll to zoom")

force = predict_downforce(speed, wing_angle)

m1, m2, m3 = st.columns(3)
m1.metric("Predicted downforce", f"{force:,.1f} N")
m2.metric("Vehicle speed", f"{speed} km/h")
m3.metric("Rear wing", f"{wing_angle}°")

st.caption(
    "Use your trained model for actual predictions. "
    "The animated airflow is a visual approximation, not CFD."
)

# =========================================================
# THREE.JS APPLICATION
# =========================================================

# JSON safely passes Streamlit settings to the browser.
settings = json.dumps({
    "speed": speed,
    "wingAngle": wing_angle,
    "streamlines": show_streamlines,
    "particles": show_particles,
    "tunnel": show_tunnel,
    "car": show_car,
    "camera": camera,
})

page = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing:border-box; }
html,body {
    margin:0; width:100%; height:100%;
    overflow:hidden; background:#07111d;
    font-family:Arial,sans-serif;
}
#viewport { position:absolute; inset:0; }
canvas { display:block; }
#badge {
    position:absolute; top:14px; left:15px;
    padding:10px 13px; border-radius:7px;
    color:#bfeeff; font-size:12px; letter-spacing:1.3px;
    background:rgba(4,17,30,.8);
    border:1px solid rgba(62,173,230,.3);
    pointer-events:none;
}
#actions {
    position:absolute; bottom:15px; left:50%;
    transform:translateX(-50%);
    display:flex; gap:7px; flex-wrap:wrap;
    justify-content:center; width:95%;
}
button {
    color:#d9f0ff; background:rgba(9,30,48,.92);
    border:1px solid #285576; border-radius:6px;
    padding:9px 13px; cursor:pointer;
}
button:hover,button.active {
    background:#087fae; border-color:#35c9ff;
}
#legend {
    position:absolute; bottom:17px; left:14px;
    color:#a7c4d9; font-size:11px;
    background:rgba(4,17,30,.75); padding:10px;
    border-radius:6px; pointer-events:none;
}
.gradient {
    height:6px; width:135px; margin-top:7px;
    background:linear-gradient(90deg,#168dff,#13e9ff,#83f27a,#ffe84a,#ff522c);
    border-radius:8px;
}
#hint {
    position:absolute; top:16px; right:15px;
    font-size:11px; color:#9abbd4;
    background:rgba(4,17,30,.75); padding:9px;
    border-radius:6px; pointer-events:none;
}
</style>
</head>
<body>
<div id="viewport"></div>
<div id="badge">● LIVE RENDER &nbsp; / &nbsp; WIND TUNNEL</div>
<div id="hint">DRAG TO ROTATE · SCROLL TO ZOOM</div>
<div id="legend">
  AIRFLOW VELOCITY (ILLUSTRATIVE)
  <div class="gradient"></div>
  <div style="display:flex;justify-content:space-between;margin-top:4px">
    <span>Low</span><span>High</span>
  </div>
</div>
<div id="actions">
  <button id="play" class="active">❚❚ Pause</button>
  <button data-camera="Three-quarter">3D view</button>
  <button data-camera="Side">Side</button>
  <button data-camera="Front">Front</button>
  <button data-camera="Top">Top</button>
  <button id="reset">↻ Reset camera</button>
</div>

<script type="module">
import * as THREE from
  'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js';
import { OrbitControls } from
  'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js';

const CFG = __SETTINGS__;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111d);
scene.fog = new THREE.FogExp2(0x07111d, 0.025);

const camera = new THREE.PerspectiveCamera(
  43, innerWidth / innerHeight, 0.1, 150
);
camera.position.set(7.6, 6.1, 7.8);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance"
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.8));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
document.getElementById("viewport").appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.8, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.minDistance = 4;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.48;

// ---------------- LIGHTING ----------------

scene.add(new THREE.HemisphereLight(0xaadfff, 0x101a28, 2.0));

const keyLight = new THREE.DirectionalLight(0xe4f4ff, 3.1);
keyLight.position.set(-3, 8, 5);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(1024, 1024);
scene.add(keyLight);

const rimLight = new THREE.PointLight(0x168bff, 65, 20);
rimLight.position.set(2, 4, -3);
scene.add(rimLight);

const warmLight = new THREE.PointLight(0xff9d52, 22, 15);
warmLight.position.set(-4, 3, 2);
scene.add(warmLight);

// ---------------- MATERIALS ----------------

const carbon = new THREE.MeshStandardMaterial({
  color: 0x101b27, metalness: 0.8, roughness: 0.28
});
const bodyMat = new THREE.MeshStandardMaterial({
  color: 0x087fa7, metalness: 0.72, roughness: 0.24
});
const redMat = new THREE.MeshStandardMaterial({
  color: 0xd82f4d, metalness: 0.6, roughness: 0.3
});
const rubber = new THREE.MeshStandardMaterial({
  color: 0x090c11, roughness: 0.84, metalness: 0.05
});
const metal = new THREE.MeshStandardMaterial({
  color: 0x8295a7, metalness: 0.9, roughness: 0.25
});

// ---------------- FLOOR AND TUNNEL ----------------

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(22, 12),
  new THREE.MeshStandardMaterial({
    color: 0x152536, metalness: 0.45, roughness: 0.38
  })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.04;
floor.receiveShadow = true;
scene.add(floor);

// Floor grid gives scale and a polished lab appearance.
const grid = new THREE.GridHelper(20, 40, 0x286080, 0x16364b);
grid.position.y = -0.025;
scene.add(grid);

const tunnelGroup = new THREE.Group();
scene.add(tunnelGroup);

function addBeam(a, b, radius=0.025, color=0x2d5d7c) {
  const start = new THREE.Vector3(...a);
  const end = new THREE.Vector3(...b);
  const direction = new THREE.Vector3().subVectors(end,start);
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radius,radius,direction.length(),8),
    new THREE.MeshStandardMaterial({
      color, metalness:0.55, roughness:0.4
    })
  );
  mesh.position.copy(start).add(end).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0,1,0), direction.normalize()
  );
  tunnelGroup.add(mesh);
}

const xmin=-5.8, xmax=5.8, ymin=0, ymax=3.6, zmin=-2.7, zmax=2.7;
for (const x of [xmin,xmax]) {
  for (const z of [zmin,zmax]) {
    addBeam([x,ymin,z],[x,ymax,z]);
  }
}
for (const y of [ymin,ymax]) {
  for (const z of [zmin,zmax]) {
    addBeam([xmin,y,z],[xmax,y,z]);
  }
  for (const x of [xmin,xmax]) {
    addBeam([x,y,zmin],[x,y,zmax]);
  }
}

// Semi-transparent side panels.
const glass = new THREE.MeshPhysicalMaterial({
  color:0x357ba0, transparent:true, opacity:0.055,
  roughness:0.16, metalness:0.2, side:THREE.DoubleSide
});
for (const z of [zmin,zmax]) {
  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(xmax-xmin,ymax-ymin), glass
  );
  panel.position.set(0,ymax/2,z);
  tunnelGroup.add(panel);
}

// ---------------- RACE CAR ----------------

// Car longitudinal axis is X; front points toward negative X.
const car = new THREE.Group();
scene.add(car);

function box(parent, size, pos, mat, bevel=false) {
  const geometry = new THREE.BoxGeometry(...size);
  const mesh = new THREE.Mesh(geometry,mat);
  mesh.position.set(...pos);
  mesh.castShadow=true;
  mesh.receiveShadow=true;
  parent.add(mesh);
  return mesh;
}

function cylinderBetween(parent, a, b, radius, material) {
  const va = new THREE.Vector3(...a);
  const vb = new THREE.Vector3(...b);
  const d = new THREE.Vector3().subVectors(vb,va);
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radius,radius,d.length(),12),
    material
  );
  mesh.position.copy(va).add(vb).multiplyScalar(.5);
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0,1,0), d.normalize()
  );
  parent.add(mesh);
  mesh.castShadow=true;
  return mesh;
}

// Undertray, sidepods, and sculpted central body.
box(car,[2.75,.20,.82],[0,.47,0],carbon);
box(car,[1.7,.28,1.08],[.30,.63,0],bodyMat);
box(car,[1.1,.17,.45],[-.92,.59,0],redMat);

// Tapered nose using a custom smooth shape.
const noseShape = new THREE.Shape();
noseShape.moveTo(-1.95,-.22);
noseShape.lineTo(-1.15,-.34);
noseShape.lineTo(-.78,-.24);
noseShape.lineTo(-.78,.24);
noseShape.lineTo(-1.15,.34);
noseShape.lineTo(-1.95,.22);
noseShape.close();

const noseGeo = new THREE.ExtrudeGeometry(noseShape,{
  depth:.16, bevelEnabled:true, bevelSegments:3,
  steps:1, bevelSize:.055, bevelThickness:.045
});
noseGeo.rotateX(Math.PI/2);
const nose = new THREE.Mesh(noseGeo,redMat);
nose.position.set(0,.72,.08);
nose.castShadow=true;
car.add(nose);

// Cockpit tub and driver protection.
box(car,[.92,.34,.63],[.12,.79,0],carbon);
const cockpit = new THREE.Mesh(
  new THREE.SphereGeometry(.31,24,16),
  new THREE.MeshPhysicalMaterial({
    color:0x0a1722, metalness:.6, roughness:.12,
    clearcoat:1, clearcoatRoughness:.1
  })
);
cockpit.scale.set(1.1,.68,.82);
cockpit.position.set(.12,.99,0);
car.add(cockpit);

cylinderBetween(car,[.13,.97,-.32],[.13,1.36,-.32],.025,metal);
cylinderBetween(car,[.13,.97,.32],[.13,1.36,.32],.025,metal);
cylinderBetween(car,[.13,1.36,-.32],[.13,1.36,.32],.025,metal);

// Rear engine cover.
box(car,[.95,.30,.64],[.95,.73,0],bodyMat);

// Wheels with sidewalls and visible hubs.
const wheels=[];
function wheel(x,z) {
  const group=new THREE.Group();
  group.position.set(x,.48,z);
  const tire=new THREE.Mesh(
    new THREE.CylinderGeometry(.39,.39,.24,40),
    rubber
  );
  tire.rotation.x=Math.PI/2;
  tire.castShadow=true;
  group.add(tire);

  const hub=new THREE.Mesh(
    new THREE.CylinderGeometry(.19,.19,.255,32),
    metal
  );
  hub.rotation.x=Math.PI/2;
  group.add(hub);

  const center=new THREE.Mesh(
    new THREE.CylinderGeometry(.07,.07,.27,24),
    carbon
  );
  center.rotation.x=Math.PI/2;
  group.add(center);

  for(let i=0;i<8;i++){
    const a=i*Math.PI/4;
    const spoke=box(group,[.025,.025,.24],
      [.09*Math.cos(a),.09*Math.sin(a),0],metal);
    spoke.rotation.z=a;
  }

  car.add(group);
  wheels.push(group);
}
wheel(-1.25,-.76); wheel(-1.25,.76);
wheel(1.0,-.88); wheel(1.0,.88);

// Suspension arms.
for(const z of [-.72,.72]){
  cylinderBetween(car,[-1.25,.53,z],[ -.75,.68,z*.55],.035,metal);
  cylinderBetween(car,[1,.53,z],[.48,.65,z*.55],.035,metal);
}

// Front wing.
box(car,[.18,.085,1.95],[-1.84,.53,0],redMat);
box(car,[.24,.08,1.65],[-1.75,.64,0],carbon);

// Rear wing assembly; rotate the actual wing with the angle control.
const rearWing=new THREE.Group();
rearWing.position.set(1.55,1.32,0);
car.add(rearWing);
box(rearWing,[.13,.085,1.50],[0,.22,0],carbon);
const wingBlade=box(rearWing,[.30,.09,1.42],[0,.02,0],redMat);
wingBlade.rotation.z=THREE.MathUtils.degToRad(CFG.wingAngle);

// Endplates.
for(const z of [-.72,.72]){
  box(rearWing,[.25,.32,.045],[0,.12,z],bodyMat);
}

// ---------------- AIRFLOW ----------------

const flowGroup=new THREE.Group();
scene.add(flowGroup);
const particleGroup=new THREE.Group();
scene.add(particleGroup);

const palette=[
  new THREE.Color(0x087cff),
  new THREE.Color(0x12e6ff),
  new THREE.Color(0x69ffb0),
  new THREE.Color(0xffe54a),
  new THREE.Color(0xff512f)
];

function flowColor(t){
  const scaled=THREE.MathUtils.clamp(t,0,.999)*4;
  const i=Math.floor(scaled);
  return palette[i].clone().lerp(palette[i+1],scaled-i);
}

// Curved streamlines flow around the car and wake.
const streamlineObjects=[];
const lineCount=30;
const pointsPerLine=160;

function streamlinePoint(t, row, phase=0){
  const x=-5.65+t*11.3;
  const z0=-2.25+row*(4.5/(lineCount-1));
  const y0=.35+((row*7)%11)*.23;

  const nearBody=Math.exp(-Math.pow((x+.1)/1.5,2));
  const vertical= .42*nearBody*Math.exp(-Math.pow((z0-.15)/1.05,2));

  // Deflection around the chassis and rear wing.
  let y=y0+vertical;
  const wake=Math.max(0,x-1.5);
  y+=.13*Math.sin(wake*3+row*.8+phase)*Math.exp(-wake*.12);
  const z=z0+.13*Math.sin(x*1.4+row*.65+phase)*nearBody;

  return new THREE.Vector3(x,y,z);
}

function createStreamlines(){
  for(let row=0;row<lineCount;row++){
    const points=[];
    const colors=[];
    for(let j=0;j<pointsPerLine;j++){
      const t=j/(pointsPerLine-1);
      points.push(streamlinePoint(t,row));
      const c=flowColor(.08+.84*Math.abs(
        Math.sin(row*.22+t*2.4)
      ));
      colors.push(c.r,c.g,c.b);
    }

    const geometry=new THREE.BufferGeometry().setFromPoints(points);
    geometry.setAttribute(
      'color',new THREE.Float32BufferAttribute(colors,3)
    );
    const material=new THREE.LineBasicMaterial({
      vertexColors:true, transparent:true, opacity:.68
    });
    const line=new THREE.Line(geometry,material);
    flowGroup.add(line);
    streamlineObjects.push({line,row});
  }
}
createStreamlines();

// A large population of small luminous particles.
const particleCount=1800;
const positions=new Float32Array(particleCount*3);
const particleColors=new Float32Array(particleCount*3);
const particleData=[];

let seed=817;
function random(){
  seed=(seed*1664525+1013904223)>>>0;
  return seed/4294967296;
}

for(let i=0;i<particleCount;i++){
  const p={
    x:-5.7+random()*11.4,
    y:.25+random()*3.0,
    z:-2.45+random()*4.9,
    phase:random()*Math.PI*2,
    speed:.65+random()*.7,
    colorT:random()
  };
  particleData.push(p);
  const c=flowColor(p.colorT);
  particleColors.set([c.r,c.g,c.b],i*3);
}

const particleGeo=new THREE.BufferGeometry();
particleGeo.setAttribute(
  'position',new THREE.BufferAttribute(positions,3)
);
particleGeo.setAttribute(
  'color',new THREE.BufferAttribute(particleColors,3)
);
const particleMat=new THREE.PointsMaterial({
  size:.035, vertexColors:true, transparent:true,
  opacity:.9, depthWrite:false, sizeAttenuation:true
});
const particles=new THREE.Points(particleGeo,particleMat);
particleGroup.add(particles);

// ---------------- SETTINGS AND CAMERAS ----------------

if(!CFG.car) car.visible=false;
if(!CFG.tunnel) tunnelGroup.visible=false;
if(!CFG.streamlines) flowGroup.visible=false;
if(!CFG.particles) particleGroup.visible=false;

function setCamera(mode){
  const positions={
    "Three-quarter":[7.6,6.1,7.8],
    "Side":[0.15,2.0,10.8],
    "Front":[-10.8,2.3,0.1],
    "Top":[.1,12,.1],
    "Rear":[10.8,2.4,.1]
  };
  const p=positions[mode]||positions["Three-quarter"];
  camera.position.set(...p);
  controls.target.set(0,.8,0);
  controls.update();
}
setCamera(CFG.camera);

document.querySelectorAll('[data-camera]').forEach(button=>{
  button.addEventListener('click',()=>{
    setCamera(button.dataset.camera);
  });
});

document.getElementById('reset').addEventListener('click',()=>{
  setCamera("Three-quarter");
});

let playing=true;
document.getElementById('play').addEventListener('click',event=>{
  playing=!playing;
  event.currentTarget.textContent=playing?'❚❚ Pause':'▶ Play';
  event.currentTarget.classList.toggle('active',playing);
});

// ---------------- CONTINUOUS ANIMATION ----------------

let elapsed=0;
const clock=new THREE.Clock();

function animate(){
  requestAnimationFrame(animate);

  // Clamp frame delta to prevent jumps after tab switching.
  const dt=Math.min(clock.getDelta(),.04);
  if(playing) elapsed+=dt;

  const flowRate=(CFG.speed/180)*.72;

  for(let i=0;i<particleCount;i++){
    const p=particleData[i];
    const t=((p.x+5.7+elapsed*flowRate*p.speed)%11.4);
    const x=t-5.7;

    const nearBody=Math.exp(-Math.pow((x+.1)/1.5,2));
    const z=p.z+.35*nearBody*
      Math.exp(-Math.pow((p.z-.05)/1.0,2));

    const wake=Math.max(0,x-1.5);
    const y=p.y+
      .11*Math.sin(wake*3+p.phase+elapsed*1.5)*
      Math.exp(-wake*.10);

    positions[3*i]=x;
    positions[3*i+1]=y;
    positions[3*i+2]=z;
  }

  particleGeo.attributes.position.needsUpdate=true;

  // Gently pulse flow ribbons to suggest motion.
  for(const item of streamlineObjects){
    item.line.material.opacity=
      .52+.16*Math.sin(elapsed*2+item.row*.4);
  }

  controls.update();
  renderer.render(scene,camera);
}

function resize(){
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
}
window.addEventListener('resize',resize);
animate();
</script>
</body>
</html>
"""

page = page.replace("__SETTINGS__", settings)

components.html(
    page,
    height=760,
    scrolling=False,
)
