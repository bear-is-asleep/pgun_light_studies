import subprocess
from multiprocessing import Pool
import csv
import time
import os
import tempfile
import shutil

base_dir = os.path.dirname(os.path.realpath(__file__))
top_dir = "/exp/sbnd/data/users/brindenc/ML/fmatch/validation/"

# Constants
num_processes = 16
p = 1.0
pdg = 13
x = -100
y = 0
z = 10
t = 0
n = 3
fcl_file = f"{top_dir}pgun_base.fcl"
run = 2101

# Grid points
thetaxzs = [-80, -60, -40, -20, 0, 20, 40, 60, 80, ]
thetayzs = [-80, -60, -40, -20, 0, 20, 40, 60, 80, ]

def log_to_csv(run_number, n, pdg, p, x, y, z, thetaxz, thetayz, t):
    with open('simulation_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['run', 'n', 'pdg', 'p', 'x', 'y', 'z', 'thetaxz', 'thetayz', 't'])
        writer.writerow([run_number, n, pdg, p, x, y, z, thetaxz, thetayz, t])

def run_simulation(params):
    thetaxz, thetayz, run_number = params
    
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

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Modify a temporary fcl file
        _fcl_file = f"{temp_dir}/pgun_base.fcl"
        shutil.copy(fcl_file, _fcl_file)
        
        subprocess.run(f"sed -i 's|outputs.out1.fileName: \".*\"|outputs.out1.fileName: \"{prod_file}.root\"|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|source.firstRun: .*|source.firstRun: {run_number}|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.PDG: \[.*\]|physics.producers.generator.PDG: [{pdg}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.X0: \[.*\]|physics.producers.generator.X0: [{x}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.Y0: \[.*\]|physics.producers.generator.Y0: [{y}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.Z0: \[.*\]|physics.producers.generator.Z0: [{z}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.P0: \[.*\]|physics.producers.generator.P0: [{p}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.Theta0XZ: \[.*\]|physics.producers.generator.Theta0XZ: [{thetaxz}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.Theta0YZ: \[.*\]|physics.producers.generator.Theta0YZ: [{thetayz}]|' {_fcl_file}", shell=True)
        subprocess.run(f"sed -i 's|physics.producers.generator.T0: \[.*\]|physics.producers.generator.T0: [{t}]|' {_fcl_file}", shell=True)

        # Run the simulation commands
        subprocess.run(["lar", "-c", _fcl_file, "-n", str(n)])
        subprocess.run(["lar", "-c", "g4_sce_lite.fcl", "-s", f"{prod_file}.root"])
        subprocess.run(f"lar -c {top_dir}detsim_keep.fcl -s {temp_dir}/{prod_file}_G4*.root", shell=True)
        subprocess.run(f"lar -c {top_dir}reco1_keep.fcl -s {temp_dir}/{prod_file}_G4*DetSim*.root", shell=True)
        subprocess.run(f"lar -c {top_dir}run_pdsana.fcl -s {temp_dir}/{prod_file}_G4*DetSim*Reco1*.root", shell=True)
        
        # Move files
        subprocess.run(["mv", "larcv.root", larcv_file])
        subprocess.run(["mv", "opana_tree.root", opsana_file])
        subprocess.run(f"mv opana*.root larcv_*.root {base_dir}/data2/", shell=True)

        # Clean up
        subprocess.run("rm *.root", shell=True)
        subprocess.run("rm *.db", shell=True)
    
    
    #Log to csv
    os.chdir(base_dir)
    log_to_csv(run_number, n, pdg, p, x, y, z, thetaxz, thetayz, t)

if __name__ == "__main__":
    with Pool(num_processes) as pool:
        pool.map(run_simulation, [(thetaxz, thetayz, run + i + 1) for i, (thetaxz, thetayz) in enumerate([(thetaxz, thetayz) for thetaxz in thetaxzs for thetayz in thetayzs])])