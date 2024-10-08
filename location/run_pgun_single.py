import subprocess
from multiprocessing import Pool
import csv
import time
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

# Constants
num_processes = 4
p = 1.0
pdg = 13
y = 210
thetaxz = 0
thetayz = -90
t = 0
n = 1
fcl_file = "../pgun_base.fcl"
run = 1000

# Grid points
xs = [-190, -170]#, -150, -130, -110, -90, -70, -50, -30, -10, 10, 30, 50, 70, 90, 110, 130, 150, 170, 190]
zs = [10, 30]#, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230, 250, 270, 290, 310, 330, 350, 370, 390, 410, 430, 450, 470, 490]

def log_to_csv(run_number, n, pdg, p, x, y, z, thetaxz, thetayz, t):
    with open('simulation_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['run', 'n', 'pdg', 'p', 'x', 'y', 'z', 'thetaxz', 'thetayz', 't'])
        writer.writerow([run_number, pdg, p, x, y, z, thetaxz, thetayz, t])

def run_simulation(params):
    x, z, run_number = params
    
    # File names
    suffix = f"pdg{pdg}_P{p}_X{x}_Y{y}_Z{z}_thetaxz{thetaxz}_thetayz{thetayz}_t{t}"
    opsana_file = f"opana_{suffix}.root"
    larcv_file = f"larcv_{suffix}.root"
    prod_file = f"prodsingle_sbnd_{suffix}"
    

    # Check if file exists
    if subprocess.run(["test", "-f", f"data2/{opsana_file}"]).returncode == 0:
        print(f"File {opsana_file} already exists, skipping...")
        return

    print("******************************")
    print(f"Starting run {run_number}")
    print(f" - {n} events for pdg {pdg}, p0 {p}, x {x}, y {y}, z {z}, thetaxz {thetaxz}, thetayz {thetayz}, t {t}")
    print("******************************")

    # Modify the fcl file
    #subprocess.run(["sed", "-i", f's/(outputs.out1.fileName: ).*/\1"{prod_file}.root"/', fcl_file])
    subprocess.run(f"sed -i 's|outputs.out1.fileName: \".*\"|outputs.out1.fileName: \"{prod_file}.root\"|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|source.firstRun: .*|source.firstRun: {run_number}|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.PDG: \[.*\]|physics.producers.generator.PDG: [{pdg}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.X0: \[.*\]|physics.producers.generator.X0: [{x}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.Y0: \[.*\]|physics.producers.generator.Y0: [{y}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.Z0: \[.*\]|physics.producers.generator.Z0: [{z}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.P0: \[.*\]|physics.producers.generator.P0: [{p}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.Theta0XZ: \[.*\]|physics.producers.generator.Theta0XZ: [{thetaxz}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.Theta0YZ: \[.*\]|physics.producers.generator.Theta0YZ: [{thetayz}]|' {fcl_file}", shell=True)
    subprocess.run(f"sed -i 's|physics.producers.generator.T0: \[.*\]|physics.producers.generator.T0: [{t}]|' {fcl_file}", shell=True)

    # Run the simulation commands
    subprocess.run(["lar", "-c", fcl_file, "-n", str(n)])
    subprocess.run(["lar", "-c", "g4_sce_lite.fcl", "-s", f"{prod_file}.root"])
    subprocess.run(f"lar -c ../detsim_keep.fcl -s {base_dir}/{prod_file}_G4*.root", shell=True)
    subprocess.run(f"lar -c ../reco1_keep.fcl -s {base_dir}/{prod_file}_G4*DetSim*.root", shell=True)
    subprocess.run(f"lar -c ../run_pdsana.fcl -s {base_dir}/{prod_file}_G4*DetSim*Reco1*.root", shell=True)
    
    # Move files
    subprocess.run(["mv", "larcv.root", larcv_file])
    subprocess.run(["mv", "opana_tree.root", opsana_file])
    subprocess.run("mv opana*.root larcv_*.root data2/", shell=True)

    # Clean up
    subprocess.run("rm *.root", shell=True)
    subprocess.run("rm *.db", shell=True)
    
    #Log to csv
    log_to_csv(run_number, n, pdg, p, x, y, z, thetaxz, thetayz, t)

if __name__ == "__main__":
    with Pool(num_processes) as pool:
        pool.map(run_simulation, [(x, z, run + i + 1) for i, (x, z) in enumerate([(x, z) for x in xs for z in zs])])