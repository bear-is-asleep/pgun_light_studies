#!/bin/bash

# xs=(-190 -180 -170 -160 -150 -140 -130 -120 -110 -100 -90 -80 -70 -60 -50 -40 -30 -20 -10 0 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190)
# zs=(10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190 200 210 220 230 240 250 260 270 280 290 300 310 320 330 340 350 360 370 380 390 400 410 420 430 440 450 460 470 480 490)
xs=(-190 -170 -150 -130 -110 -90 -70 -50 -30 -10 10 30 50 70 90 110 130 150 170 190)
zs=(10 30 50 70 90 110 130 150 170 190 210 230 250 270 290 310 330 350 370 390 410 430 450 470 490)
# xs=(0)
# zs=(210)

#Constants
p=1.0
pdg=13
y=210
thetaxz=0
thetayz=-90
t=0
n=5

fcl_file="../pgun_base.fcl"

#Set counter
run=1000

for x in ${xs[@]}; do
    for z in ${zs[@]}; do
        #Establish names
        suffix="pdg${pdg}_P${p}_X${x}_Y${y}_Z${z}_thetaxz${thetaxz}_thetayz${thetayz}_t${t}"

        #Increment counter
        run=$((run+1))
        # Check if opsana root file exists
        opsana_file="opana_${suffix}.root"
        larcv_file="larcv_${suffix}.root"
        prod_file="prodsingle_sbnd_${suffix}"

        if [ -f "data/$opsana_file" ]; then
            echo "File $opsana_file already exists, skipping..."
            continue
        fi
        echo "******************************"
        echo "Running $n events for pdg $pdg, p0 $p, x $x, y $y, z $z, thetaxz $thetaxz, thetayz $thetayz, t $t"
        echo "******************************"
        sed -i 's/\(outputs.out1.fileName: \).*\$/\1\"${prod_file}.root\"/' $fcl_file
        sed -i "s/\(source.firstRun: \).*\$/\1$run/" $fcl_file
        sed -i "s/\(physics.producers.generator.PDG: \)\[.*\]/\1\[$pdg\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.X0: \)\[.*\]/\1\[$x\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.Y0: \)\[.*\]/\1\[$y\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.Z0: \)\[.*\]/\1\[$z\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.P0: \)\[.*\]/\1\[$p\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.Theta0XZ: \)\[.*\]/\1\[$thetaxz\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.Theta0YZ: \)\[.*\]/\1\[$thetayz\]/" $fcl_file
        sed -i "s/\(physics.producers.generator.T0: \)\[.*\]/\1\[$t\]/" $fcl_file

        cat $fcl_file
        echo "******************************"

        #Run larsoft
        lar -c $fcl_file -n $n
        sleep 1s
        lar -c g4_sce_lite.fcl -s ${prod_file}.root
        sleep 1s
        lar -c ../detsim_keep.fcl -s ${prod_file}*_G4*.root
        sleep 1s
        lar -c ../reco1_keep.fcl -s ${prod_file}*_G4*_DetSim*.root
        sleep 1s
        lar -c ../run_pdsana.fcl -s ${prod_file}*_G4*_DetSim*.root
        sleep 1s
        mv larcv.root "$larcv_file"
        sleep 1s
        mv opana_tree.root "$opsana_file"

        #Clean up
        rm prodsingle_sbnd_SinglesGen*.root
        rm hist*.root
        rm *.db
        mv opana*.root larcv_*.root data/ #move to data folder
    done
done



