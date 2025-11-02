# Tutorial: Membuat Animasi Tank Menembak Missile di Blender dengan Python

## Daftar Isi
1. [Pengenalan](#pengenalan)
2. [Persiapan](#persiapan)
3. [Konsep Dasar Animasi](#konsep-dasar-animasi)
4. [Langkah 1: Membersihkan Scene](#langkah-1-membersihkan-scene)
5. [Langkah 2: Membuat Material System](#langkah-2-membuat-material-system)
6. [Langkah 3: Membuat Tank](#langkah-3-membuat-tank)
7. [Langkah 4: Membuat Target](#langkah-4-membuat-target)
8. [Langkah 5: Membuat Missile](#langkah-5-membuat-missile)
9. [Langkah 6: Animasi Turret Rotation](#langkah-6-animasi-turret-rotation)
10. [Langkah 7: Animasi Missile](#langkah-7-animasi-missile)
11. [Langkah 8: Sistem Partikel Debu](#langkah-8-sistem-partikel-debu)
12. [Langkah 9: Ground, Lighting, dan Camera](#langkah-9-ground-lighting-dan-camera)
13. [Langkah 10: Timeline dan Koordinasi](#langkah-10-timeline-dan-koordinasi)
14. [Tips Debugging](#tips-debugging)
15. [Customization Ideas](#customization-ideas)

---

## Pengenalan

Tutorial ini mengajarkan cara membuat animasi tank militer yang menembak 5 target dengan missile. Fitur animasi:

🎯 **Fitur Utama:**
- Tank dengan body, turret yang berputar, dan barrel (laras)
- 5 target berwarna tersusun dalam arc (lengkungan)
- Turret otomatis menghadap target sebelum menembak
- Missile terbang dari barrel ke target
- Efek ledakan partikel debu saat impact
- Target menghilang setelah terkena

**Konsep Yang Akan Dipelajari:**
- **Hierarchi Objek**: Parent-child relationship untuk tank parts
- **Trigonometri**: Menghitung sudut rotasi turret
- **Keyframe Animation**: Animasi manual untuk kontrol presisi
- **Particle System**: Efek visual ledakan
- **Koordinasi Timeline**: Multiple animasi yang sinkron

---

## Persiapan

### Kebutuhan:
- **Blender 4.3** atau lebih baru
- **Python** (built-in di Blender)
- Pemahaman dasar matematika (sinus, cosinus, atan2)

### Struktur Animasi Timeline:

```
Frame 1-50:    Target 1 (Fire frame 1 → Impact frame 31)
Frame 51-100:  Target 2 (Fire frame 51 → Impact frame 81)
Frame 101-150: Target 3 (Fire frame 101 → Impact frame 131)
Frame 151-200: Target 4 (Fire frame 151 → Impact frame 181)
Frame 201-250: Target 5 (Fire frame 201 → Impact frame 231)
```

**Interval:** 50 frame per missile (2.08 detik pada 24 fps)

---

## Konsep Dasar Animasi

### Hierarchi Tank (Parent-Child):

```
TankBody (Parent)
├── TankTurret (Child of Body)
│   └── TankBarrel (Child of Turret)
├── LeftTrack (Child of Body)
└── RightTrack (Child of Body)
```

**Keuntungan Hierarchi:**
- Gerakkan body → semua parts ikut bergerak
- Putar turret → hanya turret dan barrel yang ikut
- Animasi lebih mudah dan konsisten

### Koordinat System:

```
     Z (atas)
     |
     |_____ Y (depan)
    /
   X (kanan)
```

- **X-axis**: Kiri (-) ke Kanan (+)
- **Y-axis**: Belakang (-) ke Depan (+)
- **Z-axis**: Bawah (-) ke Atas (+)

---

## Langkah 1: Membersihkan Scene

```python
def clear_scene():
    """Remove all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear orphaned data
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
```

**Penjelasan:**
1. `select_all`: Pilih semua objek
2. `delete`: Hapus objek yang dipilih
3. **Orphaned Data**: Data material/mesh yang tidak terpakai

**Mengapa Clear Orphaned Data?**
- Mencegah memory leak
- File .blend tidak bloat
- Script bisa dijalankan berulang kali tanpa error

---

## Langkah 2: Membuat Material System

### Fungsi Create Material

```python
def create_material(name, color, roughness=0.5, metallic=0.0):
    """Create a material with specified color and properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()  # Hapus node default
```

**Parameter Material:**
- `name`: Identifier unik (misal: "TankBodyMat")
- `color`: RGBA tuple (0.0-1.0 untuk setiap channel)
- `roughness`: 0.0 = cermin, 1.0 = kasar/matte
- `metallic`: 0.0 = plastik/kayu, 1.0 = metal murni

### Setup Shader Nodes

```python
    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.location = (0, 0)
    
    # Create output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
```

**Node System:**
```
[Principled BSDF] --BSDF--> [Material Output]
```

**Location:** Posisi visual di Node Editor (tidak mempengaruhi fungsi)

### Cara Apply Material

```python
def apply_material(obj, material):
    """Apply material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material  # Replace existing
    else:
        obj.data.materials.append(material)  # Add new
```

**Logic:**
- Cek apakah objek sudah punya material
- Jika ada: replace yang pertama
- Jika tidak: tambahkan baru

---

## Langkah 3: Membuat Tank

### Tank Body (Base)

```python
def create_tank(location=(0, -10, 0)):
    """Create a simple tank with body, turret, and barrel"""
    tank_parts = []
    
    # Tank body - bottom sits on ground
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], 0))
    body = bpy.context.active_object
    body.name = "TankBody"
    body.scale = (3, 4, 1.5)  # Lebar X, Panjang Y, Tinggi Z
    body.location.z = 0.75  # Half of scaled height (1.5/2)
```

**Perhitungan Posisi Z:**
- Scale Z = 1.5 (tinggi body)
- Center harus di 1.5/2 = 0.75
- Sehingga bottom body tepat di Z=0 (ground level)

**Kenapa Scale Bukan Size?**
```python
# ❌ Sulit:
bpy.ops.mesh.primitive_cube_add(size=(3, 4, 1.5))  # Tidak bisa!

# ✅ Mudah:
bpy.ops.mesh.primitive_cube_add(size=1)
body.scale = (3, 4, 1.5)
```

### Tank Turret (Rotating Part)

```python
    # Tank turret - centered on body top
    turret_z = 0.75 + 0.75 + 0.5  # = 2.0
    # Breakdown:
    # 0.75 = body center
    # 0.75 = body top (center + half height)
    # 0.5 = turret half height
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.2, 
        depth=1, 
        location=(location[0], location[1], turret_z)
    )
    turret = bpy.context.active_object
    turret.name = "TankTurret"
```

**Pilihan Shape:**
- **Cylinder**: Bentuk turret tank yang realistis
- `radius=1.2`: Lebih besar dari body agar terlihat jelas
- `depth=1`: Tinggi turret

### Tank Barrel (Gun)

```python
    # Tank barrel - attached to turret front
    barrel_z = turret_z  # Same height as turret center
    barrel_y = location[1] + 2  # Extended forward
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.3, 
        depth=4, 
        location=(location[0], barrel_y, barrel_z)
    )
    barrel = bpy.context.active_object
    barrel.name = "TankBarrel"
    barrel.rotation_euler = (math.radians(90), 0, 0)  # Point forward
```

**Rotasi Barrel:**
- Default cylinder: vertikal (sepanjang Z-axis)
- Rotate X 90°: horizontal (sepanjang Y-axis)
- `math.radians(90)`: Konversi 90 derajat ke radian

### Parenting dengan Keep Transform

```python
    # Parent turret ke body
    bpy.context.view_layer.objects.active = body  # Set body as active
    turret.select_set(True)  # Select turret
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    turret.select_set(False)  # Deselect
    
    # Parent barrel ke turret
    bpy.context.view_layer.objects.active = turret
    barrel.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    barrel.select_set(False)
```

**Keep Transform = True:**
- Mempertahankan posisi/rotasi world space
- Tanpa ini, objek akan "loncat" ke posisi parent

**Mengapa Tidak Bisa `.parent = body`?**
```python
# ❌ Ini tidak bekerja dengan baik:
turret.parent = body  # Posisi bisa salah!

# ✅ Gunakan operator untuk keep transform:
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
```

### Tracks (Roda Tank)

```python
    # Left track
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0] - 1.8, location[1], 0))
    left_track = bpy.context.active_object
    left_track.name = "LeftTrack"
    left_track.scale = (0.5, 4.5, 0.8)  # Tipis, panjang, rendah
    left_track.location.z = 0.4  # Setengah tinggi (0.8/2)
```

**Posisi Tracks:**
- Left: X = -1.8 (di kiri body)
- Right: X = +1.8 (di kanan body)
- Keduanya parent ke body agar ikut bergerak

**Material Tracks:**
```python
    track_mat = create_material("TrackMat", (0.15, 0.15, 0.15, 1.0), 
                                roughness=0.8, metallic=0.2)
```
- Warna gelap (abu-abu tua)
- Roughness tinggi (kasar seperti karet)
- Metallic rendah (bukan metal murni)

---

## Langkah 4: Membuat Target

### Arranging Targets in Arc

```python
def create_target_objects():
    """Create 5 target objects arranged in an arc"""
    targets = []
    
    for i in range(5):
        angle = math.radians(-60 + (i * 30))  # -60° to +60°
        distance = 15
        x = distance * math.sin(angle)
        y = distance * math.cos(angle)
```

**Formula Arc:**
- Sudut: -60°, -30°, 0°, +30°, +60° (total 120° arc)
- Jarak dari origin: 15 unit
- **Trigonometri:**
  - `x = r * sin(θ)`: Posisi horizontal
  - `y = r * cos(θ)`: Posisi depth

**Visualisasi Arc:**
```
        Target 0 (-60°)
              /
             /
    Target 1 (-30°)
           |
    Target 2 (0°)  ← Tengah
           |
    Target 3 (+30°)
             \
              \
        Target 4 (+60°)
```

### Membuat Cube Target

```python
        # Create cube target
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0))
        target = bpy.context.active_object
        target.name = f"Target_{i+1}"
        target.scale = (2, 2, 3)  # Lebar, dalam, tinggi
        target.location.z = 1.5  # Bottom sits on ground
```

**Tinggi Target:**
- Scale Z = 3 (tinggi total)
- Location Z = 1.5 (half height)
- Bottom di Z=0, top di Z=3

### Material Berwarna

```python
    colors = [
        (0.8, 0.2, 0.2, 1.0),  # Merah
        (0.2, 0.8, 0.2, 1.0),  # Hijau
        (0.2, 0.2, 0.8, 1.0),  # Biru
        (0.8, 0.8, 0.2, 1.0),  # Kuning
        (0.8, 0.2, 0.8, 1.0),  # Magenta
    ]
    
    target_mat = create_material(f"TargetMat_{i+1}", colors[i], 
                                 roughness=0.4, metallic=0.1)
```

**Warna Cerah:**
- RGB values tinggi (0.8)
- Roughness rendah (agak mengkilap)
- Metallic rendah (plastik)

---

## Langkah 5: Membuat Missile

```python
def create_missile(start_location):
    """Create a missile projectile"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.2, 
        depth=1.5, 
        location=start_location
    )
    missile = bpy.context.active_object
    missile.name = "Missile"
    missile.rotation_euler = (math.radians(90), 0, 0)  # Point forward
```

**Shape Missile:**
- **Cylinder**: Bentuk roket/missile yang tipis panjang
- `radius=0.2`: Tipis (diameter 0.4)
- `depth=1.5`: Panjang missile
- Rotate X 90°: Arahkan ke depan (Y-axis)

**Material Missile:**
```python
    missile_mat = create_material("MissileMat", (0.15, 0.15, 0.15, 1.0), 
                                 roughness=0.3, metallic=0.7)
```
- Warna gelap (abu-abu tua/hitam)
- Roughness rendah (mengkilap)
- Metallic tinggi (seperti logam)

---

## Langkah 6: Animasi Turret Rotation

### Menghitung Sudut ke Target

```python
# Calculate angle to target
target_x = target.location.x
target_y = target.location.y
tank_y = tank_body.location.y

# ⚠️ PENTING: Negate angle agar turret menghadap target
angle_to_target = -math.atan2(target_x, target_y - tank_y)
```

**Formula Sudut:**
```
angle = -atan2(Δx, Δy)

Dimana:
Δx = target_x - tank_x  (tapi tank_x = 0)
Δy = target_y - tank_y
```

**Mengapa Negative (`-`)?**
- `atan2` return sudut dari sumbu +X
- Blender Z-rotation: positive = counter-clockwise
- Target di kanan (+X): perlu rotate negative (clockwise)
- Target di kiri (-X): perlu rotate positive (counter-clockwise)

**Contoh Perhitungan:**

```
Target 1: x=-12, y=7.5, tank_y=-10
Δy = 7.5 - (-10) = 17.5
angle = -atan2(-12, 17.5) = -(-34.6°) = +34.6° (putar kiri)

Target 5: x=+12, y=7.5, tank_y=-10
angle = -atan2(+12, 17.5) = -(+34.6°) = -34.6° (putar kanan)
```

### Keyframe Rotasi Turret

```python
# Start rotating 10 frames before firing
bpy.context.scene.frame_set(fire_frame - 10)

tank_turret.rotation_euler.z = 0  # Start at 0°
tank_turret.keyframe_insert(data_path="rotation_euler", frame=fire_frame - 10)

tank_turret.rotation_euler.z = angle_to_target  # End at target angle
tank_turret.keyframe_insert(data_path="rotation_euler", frame=fire_frame)
```

**Timeline Rotasi:**
```
Frame (fire_frame - 10): Turret at 0° (menghadap depan)
Frame (fire_frame):      Turret at angle_to_target (menghadap target)
                         ↓ Smooth interpolation otomatis
```

**Interpolation:**
Blender otomatis membuat smooth rotation antara 2 keyframe (bezier curve).

---

## Langkah 7: Animasi Missile

### Posisi Start Missile

```python
# Start position near barrel tip
barrel_tip_y = tank_body.location.y + 4  # 4 unit di depan tank
barrel_tip_z = tank_body.location.z + 1.5  # Ketinggian turret
missile_start = (target_x * 0.1, barrel_tip_y, barrel_tip_z)
```

**Perhitungan:**
- Y: Tank Y (-10) + 4 = -6 (ujung barrel)
- Z: Tank Z (0.75) + 1.5 = 2.25 (ketinggian turret)
- X: `target_x * 0.1` untuk sedikit offset (estetika)

### Keyframe Missile Flight

```python
# Fire frame: Missile appears at barrel
bpy.context.scene.frame_set(fire_frame)
missile.location = missile_start
missile.keyframe_insert(data_path="location", frame=fire_frame)
missile.scale = (1, 1, 1)
missile.keyframe_insert(data_path="scale", frame=fire_frame)

# Impact frame: Missile reaches target
bpy.context.scene.frame_set(impact_frame)
missile.location = target.location.copy()
missile.keyframe_insert(data_path="location", frame=impact_frame)

# Impact+1: Missile disappears
bpy.context.scene.frame_set(impact_frame + 1)
missile.scale = (0.01, 0.01, 0.01)  # Scale to near-zero
missile.keyframe_insert(data_path="scale", frame=impact_frame + 1)
```

**Timeline Missile:**
```
Frame N (fire):     Location = barrel_tip, Scale = (1,1,1) ✅ Visible
                    ↓ Flies towards target (30 frames)
Frame N+30 (impact): Location = target, Scale = (1,1,1) ✅ Visible
Frame N+31:         Location = target, Scale = (0.01,0.01,0.01) ❌ Hidden
```

**Mengapa Scale 0.01 Bukan 0?**
- Scale = 0 bisa cause crash/error
- Scale = 0.01 sangat kecil (invisible) tapi aman

### Target Disappears

```python
# Target scale animation (same timing as missile)
bpy.context.scene.frame_set(impact_frame)
target.scale = (2, 2, 3)  # Original size
target.keyframe_insert(data_path="scale", frame=impact_frame)

bpy.context.scene.frame_set(impact_frame + 1)
target.scale = (0.01, 0.01, 0.01)  # Disappear
target.keyframe_insert(data_path="scale", frame=impact_frame + 1)
```

**Efek:**
Dalam 1 frame (1/24 detik), target "menghilang" seolah hancur.

---

## Langkah 8: Sistem Partikel Debu

### Membuat Emitter

```python
def create_dust_particle_system(target, frame):
    """Create dust particle explosion at target location"""
    # Create emitter plane at target location
    location = target.location.copy()
    bpy.ops.mesh.primitive_plane_add(size=0.1, location=location)
    emitter = bpy.context.active_object
    emitter.name = f"DustEmitter_{target.name}"
```

**Emitter:**
- Plane kecil (0.1 unit) di posisi target
- Plane ini yang emit partikel
- Invisible di render (akan di-hide nanti)

### Konfigurasi Particle System

```python
    # Add particle system
    bpy.ops.object.particle_system_add()
    psys = emitter.particle_systems[0]
    pset = psys.settings
    
    # Particle settings
    pset.name = f"Dust_{target.name}"
    pset.count = 100  # Jumlah partikel
    pset.frame_start = frame  # Mulai emit di impact frame
    pset.frame_end = frame + 1  # Stop emit setelah 1 frame
    pset.lifetime = 30  # Partikel hidup 30 frame (1.25 detik)
```

**Timing Partikel:**
```
Frame N (impact):    Start emitting (burst)
Frame N+1:           Stop emitting
Frame N to N+30:     Particles visible and moving
Frame N+30:          Particles disappear
```

### Properti Fisika Partikel

```python
    pset.emit_from = 'FACE'
    pset.normal_factor = 2.0  # Spread outward (keluar dari permukaan)
    pset.factor_random = 1.5  # Randomize velocity
    
    # Physics
    pset.physics_type = 'NEWTON'  # Affected by gravity
    pset.mass = 0.1  # Light particles
    pset.particle_size = 0.15  # Size of each particle
    pset.size_random = 0.5  # Size variation
```

**Parameter Penting:**
- `normal_factor = 2.0`: Partikel meledak ke segala arah
- `factor_random = 1.5`: Kecepatan acak untuk variasi
- `mass = 0.1`: Ringan (tidak jatuh terlalu cepat)
- `particle_size = 0.15`: Ukuran partikel debu

### Gravity dan Damping

```python
    # Gravity and damping
    pset.effector_weights.gravity = 0.5  # Half gravity (debu melayang)
    pset.damping = 0.5  # Air resistance
```

**Efek:**
- `gravity = 0.5`: Partikel jatuh pelan (seperti debu)
- `damping = 0.5`: Ada hambatan udara (tidak jatuh langsung)

### Particle Instance Object

```python
    # Render settings
    pset.render_type = 'OBJECT'
    
    # Create small cube for particle instance
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(100, 100, 100))
    particle_obj = bpy.context.active_object
    particle_obj.name = f"DustParticle_{target.name}"
    
    # Color particle same as target
    if target.data.materials:
        particle_obj.data.materials.append(target.data.materials[0])
    
    pset.instance_object = particle_obj
```

**Instance Object:**
- Setiap partikel adalah instance dari cube kecil ini
- `location=(100, 100, 100)`: Jauh dari scene (tidak terlihat langsung)
- Material sama dengan target (warna matching)

**Render Type:**
- `'OBJECT'`: Render sebagai mesh object (cube)
- Alternatif: `'HALO'` (titik cahaya), `'PATH'` (streak)

---

## Langkah 9: Ground, Lighting, dan Camera

### Ground Plane

```python
def setup_ground():
    """Create ground plane"""
    bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    ground_mat = create_material("GroundMat", (0.4, 0.35, 0.3, 1.0), 
                                 roughness=0.9, metallic=0.0)
    apply_material(ground, ground_mat)
```

**Ground:**
- Size 50: Cukup besar untuk seluruh scene
- Location Z=0: Ground level
- Warna coklat muda (tanah)
- Roughness tinggi (permukaan kasar)

### Sun Lighting

```python
def setup_lighting():
    """Add lighting to the scene"""
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(30), 0)
```

**Sun Light:**
- `type='SUN'`: Directional light (parallel rays)
- `energy=3.0`: Brightness
- Rotation: 45° dari atas, 30° dari samping
- Location tidak penting untuk Sun (infinite distance)

### Camera Setup

```python
def setup_camera(tank_body):
    """Set up camera to view the scene"""
    cam_location = (0, -20, 8)  # Behind and above tank
    bpy.ops.object.camera_add(location=cam_location)
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(65), 0, 0)
    bpy.context.scene.camera = camera
```

**Camera Position:**
- X=0: Center (tidak ke kiri/kanan)
- Y=-20: Jauh di belakang tank (tank di Y=-10)
- Z=8: Tinggi untuk overview shot
- Rotation X=65°: Melihat ke bawah

**Visualisasi:**
```
        Camera (0, -20, 8)
              |
              | Looking down 65°
              ↓
         Tank (0, -10, 0.75)
              |
              | Targets spread ahead
              ↓
      Target Arc (Y = 7-15)
```

---

## Langkah 10: Timeline dan Koordinasi

### Main Animation Loop

```python
def animate_tank_missile_destruction():
    # ... setup ...
    
    # Animation timing
    missile_intervals = 50  # Jarak antar missile
    
    for i, target in enumerate(targets):
        fire_frame = 1 + (i * missile_intervals)
        impact_frame = fire_frame + 30  # 30 frames flight time
```

**Timeline Calculation:**
```
Target 0: fire_frame = 1,   impact_frame = 31
Target 1: fire_frame = 51,  impact_frame = 81
Target 2: fire_frame = 101, impact_frame = 131
Target 3: fire_frame = 151, impact_frame = 181
Target 4: fire_frame = 201, impact_frame = 231
```

### Koordinasi Semua Animasi

Untuk setiap target, sequence yang terjadi:

```python
# 1. Turret Rotation (frame - 10 to frame)
bpy.context.scene.frame_set(fire_frame - 10)
tank_turret.rotation_euler.z = 0
tank_turret.keyframe_insert(...)

bpy.context.scene.frame_set(fire_frame)
tank_turret.rotation_euler.z = angle_to_target
tank_turret.keyframe_insert(...)

# 2. Missile Launch (fire_frame)
missile.location = missile_start
missile.keyframe_insert(...)

# 3. Missile Flight (fire_frame to impact_frame)
missile.location = target.location
missile.keyframe_insert(...)

# 4. Impact Effects (impact_frame)
# - Missile disappears
missile.scale = (0.01, 0.01, 0.01)
missile.keyframe_insert(...)

# - Target disappears
target.scale = (0.01, 0.01, 0.01)
target.keyframe_insert(...)

# - Particles spawn
emitter, particle_obj = create_dust_particle_system(target, impact_frame)
```

**Timeline Visual:**
```
Missile 1:  [====Rotate====][======Fly======][X] [--Particles--]
              -10 → 1       1 → 31          31  31 → 61

Missile 2:                        [====Rotate====][======Fly======][X]
                                    41 → 51       51 → 81          81
```

### Frame Range Setting

```python
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 300
    bpy.context.scene.frame_set(1)
```

**Settings:**
- FPS: 24 (standard film)
- Frame 1-300: 12.5 detik total
- `frame_set(1)`: Reset timeline ke frame 1

---

## Tips Debugging

### 1. Print Timeline Info

```python
print("\nTIMELINE:")
for i in range(5):
    fire = 1 + (i * missile_intervals)
    impact = fire + 30
    print(f"  Target {i+1}: Fire frame {fire} → Impact frame {impact}")
```

**Output:**
```
TIMELINE:
  Target 1: Fire frame 1 → Impact frame 31
  Target 2: Fire frame 51 → Impact frame 81
  ...
```

### 2. Verify Turret Angle

```python
# Add debug print
angle_degrees = math.degrees(angle_to_target)
print(f"Target {i+1}: Angle = {angle_degrees:.1f}°")
```

### 3. Check Object Positions

```python
# After creating tank
print(f"Tank body: {tank_body.location}")
print(f"Tank turret: {tank_turret.location}")
print(f"Tank barrel: {tank_barrel.location}")

# After creating targets
for i, target in enumerate(targets):
    print(f"Target {i+1}: X={target.location.x:.2f}, Y={target.location.y:.2f}")
```

### 4. Test dengan Satu Target

```python
# Ubah loop untuk test
for i, target in enumerate(targets[:1]):  # Only first target
    # ... animation code ...
```

### 5. Slow Motion untuk Debug

```python
missile_intervals = 100  # Dari 50 jadi 100 (lebih lambat)
```

---

## Customization Ideas

### 1. Lebih Banyak Target

```python
def create_target_objects():
    num_targets = 10  # Dari 5 jadi 10
    for i in range(num_targets):
        angle = math.radians(-90 + (i * (180/(num_targets-1))))
        # Spread 180° arc
```

### 2. Target Bergerak

```python
# Tambah animasi target sebelum di-shoot
for target in targets:
    # Keyframe 1: Start position
    bpy.context.scene.frame_set(1)
    target.location.x = original_x
    target.keyframe_insert(data_path="location", frame=1)
    
    # Keyframe 100: End position
    bpy.context.scene.frame_set(100)
    target.location.x = original_x + 5  # Move 5 units
    target.keyframe_insert(data_path="location", frame=100)
```

### 3. Rapid Fire Mode

```python
missile_intervals = 10  # Very fast (10 frames = 0.42 seconds)
```

### 4. Missile Trail Effect

```python
# Tambah particle trail pada missile
def add_missile_trail(missile):
    bpy.ops.object.particle_system_add()
    psys = missile.particle_systems[0]
    pset = psys.settings
    
    pset.count = 50
    pset.frame_start = 1
    pset.frame_end = 300
    pset.lifetime = 10  # Short trail
    pset.emit_from = 'VOLUME'
    pset.particle_size = 0.05
    
    # Smoke/fire material
    trail_mat = create_material("TrailMat", (1.0, 0.5, 0.0, 1.0))
    # ... apply to particles
```

### 5. Camera Animation

```python
def setup_camera(tank_body):
    # ... existing camera setup ...
    
    # Animate camera to follow action
    bpy.context.scene.frame_set(1)
    camera.location = (0, -20, 8)
    camera.keyframe_insert(data_path="location", frame=1)
    
    bpy.context.scene.frame_set(150)
    camera.location = (0, -15, 10)  # Move closer and higher
    camera.keyframe_insert(data_path="location", frame=150)
```

### 6. Explosion Effect (Advanced)

```python
# Tambah second particle system untuk api
def create_fire_explosion(target, frame):
    # ... same as dust ...
    pset.name = f"Fire_{target.name}"
    pset.particle_size = 0.3  # Bigger
    
    # Orange/yellow fire color
    fire_mat = create_material("FireMat", (1.0, 0.5, 0.0, 1.0))
    fire_mat.blend_method = 'BLEND'
    # Apply emissive shader for glow
```

### 7. Sound Effects (Konsep)

```python
# Note: Blender Python API tidak support audio langsung
# Tapi bisa add sound strips di VSE (Video Sequence Editor)

import bpy

# Add audio strip
bpy.context.scene.sequence_editor_create()
sound = bpy.context.scene.sequence_editor.sequences.new_sound(
    name="Explosion",
    filepath="//explosion.wav",
    channel=1,
    frame_start=impact_frame
)
```

### 8. Multiple Tanks

```python
# Create 2 tanks
tank1_body, tank1_turret, tank1_barrel, _ = create_tank(location=(-5, -10, 0))
tank2_body, tank2_turret, tank2_barrel, _ = create_tank(location=(5, -10, 0))

# Each tank shoots alternate targets
for i, target in enumerate(targets):
    if i % 2 == 0:
        # Tank 1 shoots even targets
        current_tank = (tank1_body, tank1_turret, tank1_barrel)
    else:
        # Tank 2 shoots odd targets
        current_tank = (tank2_body, tank2_turret, tank2_barrel)
```

---

## Troubleshooting Common Errors

### Error 1: Turret Tidak Menghadap Target

**Gejala:** Turret rotate ke arah salah

**Penyebab:** Lupa negate angle

**Solusi:**
```python
# ❌ Salah:
angle_to_target = math.atan2(target_x, target_y - tank_y)

# ✅ Benar:
angle_to_target = -math.atan2(target_x, target_y - tank_y)
```

### Error 2: Tank Parts Terpisah

**Gejala:** Turret tidak ikut saat tank bergerak

**Penyebab:** Parenting tidak benar

**Solusi:**
```python
# Pastikan keep_transform=True
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
```

### Error 3: Partikel Tidak Muncul

**Gejala:** Tidak ada efek ledakan

**Penyebab:** 
1. Instance object belum di-set
2. Viewport shading bukan 'Rendered'

**Solusi:**
```python
# Set instance object
pset.render_type = 'OBJECT'
pset.instance_object = particle_obj

# Atau gunakan viewport shading: Solid/Material Preview
```

### Error 4: Missile Tidak Kelihatan

**Gejala:** Missile exist tapi tidak visible

**Kemungkinan:**
1. Scale terlalu kecil
2. Material tidak applied
3. Behind camera

**Debug:**
```python
print(f"Missile location: {missile.location}")
print(f"Missile scale: {missile.scale}")
print(f"Missile materials: {missile.data.materials}")
```

### Error 5: Animation Lag/Slow

**Penyebab:** Terlalu banyak partikel atau samples

**Optimasi:**
```python
# Kurangi particle count
pset.count = 50  # Dari 100 jadi 50

# Kurangi particle lifetime
pset.lifetime = 20  # Dari 30 jadi 20

# Test mode: Skip particles
# add_particle_effects()  # Comment out
```

---

## Konsep Advanced

### 1. Physik Realistis (Trajectory)

Missile sebenarnya tidak terbang lurus. Dengan gravity:

```python
# Calculate ballistic trajectory
def calculate_trajectory(start, end, frames):
    """Calculate arc trajectory with gravity"""
    positions = []
    for t in range(frames):
        progress = t / frames
        
        # Linear interpolation + gravity curve
        x = start[0] + (end[0] - start[0]) * progress
        y = start[1] + (end[1] - start[1]) * progress
        z = start[2] + (end[2] - start[2]) * progress
        z -= 0.5 * 9.81 * (progress * (1 - progress))  # Parabola
        
        positions.append((x, y, z))
    
    return positions
```

### 2. LOD (Level of Detail)

Untuk scene besar, gunakan simplified mesh untuk partikel:

```python
# High-poly target untuk close-up
target_highpoly = create_cube(subdivisions=3)

# Low-poly particle untuk speed
particle_lowpoly = create_cube(subdivisions=0)
pset.instance_object = particle_lowpoly
```

### 3. Constraint Tracking

Tank turret bisa track target otomatis dengan constraint:

```python
# Add Track To constraint
bpy.context.view_layer.objects.active = tank_turret
bpy.ops.object.constraint_add(type='TRACK_TO')

constraint = tank_turret.constraints[-1]
constraint.target = target
constraint.track_axis = 'TRACK_Y'
constraint.up_axis = 'UP_Z'

# Animate constraint influence
bpy.context.scene.frame_set(fire_frame - 10)
constraint.influence = 0
constraint.keyframe_insert(data_path="influence", frame=fire_frame - 10)

bpy.context.scene.frame_set(fire_frame)
constraint.influence = 1
constraint.keyframe_insert(data_path="influence", frame=fire_frame)
```

---

## Kesimpulan

Anda telah belajar:

✅ **Hierarchi Objek Complex**
- Parent-child dengan keep_transform
- Multi-level hierarchy (body → turret → barrel)

✅ **Trigonometri untuk Rotasi**
- `atan2` untuk angle calculation
- Arc arrangement dengan sin/cos

✅ **Koordinasi Multiple Animasi**
- Timeline planning
- Sequential events dengan interval

✅ **Particle System**
- Burst emission
- Instance rendering
- Physics properties

✅ **Keyframe Animation Advanced**
- Multiple objects
- Scale untuk hide/show
- Smooth interpolation

### Next Steps

1. **Eksperimen dengan parameter**
   - Ubah interval, speed, jumlah target
   - Test different colors dan materials

2. **Add complexity**
   - Multiple tanks
   - Moving targets
   - Obstacles

3. **Improve visuals**
   - Better particle effects (fire, smoke)
   - Camera animation
   - HDR lighting

4. **Render output**
   - Setup render settings
   - Export video dengan FFMPEG

---

## Referensi

- **Blender Particle System**: https://docs.blender.org/manual/en/latest/physics/particles/
- **Parent-Child Relationship**: https://docs.blender.org/manual/en/latest/scene_layout/object/editing/parent.html
- **Keyframe Animation**: https://docs.blender.org/manual/en/latest/animation/keyframes/
- **Math Functions**: https://docs.python.org/3/library/math.html

---

**Selamat! Anda telah membuat animasi tank missile yang kompleks! 🚀🎯**

**Tips Terakhir:**
- Save script secara berkala
- Test satu target dulu sebelum semua
- Debug dengan print statements
- Have fun experimenting! 💥
