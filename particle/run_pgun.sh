#!/bin/bash

pdgs=(13 22 11 211 2212) #muon, gamma, electron, pion, proton

#Constants
p=1
pdg=13
x=-100
y=0
z=0
thetaxz=0
thetayz=0
t=0
n=10

fcl_file="../pgun_base.fcl"

#Set counter
run=3000

for pdg in ${pdgs[@]}; do
    # Check if opsana root file exists
    opsana_file="opana_pdg${pdg}_P${p}_X${x}_Y${y}_Z${z}_thetaxz${thetaxz}_thetayz${thetayz}_t${t}.root"
    if [ -f "data/$opsana_file" ]; then
        echo "File $opsana_file already exists, skipping..."
        continue
    fi
    echo "******************************"
    echo "Running $n events for pdg $pdg, p0 $p, x $x, y $y, z $z, thetaxz $thetaxz, thetayz $thetayz, t $t"
    echo "******************************"
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
    lar -c g4_sce_lite.fcl -s prodsingle_sbnd_SinglesGen*.root
    sleep 1s
    lar -c ../detsim_keep.fcl -s prodsingle_sbnd_SinglesGen*_G4*.root
    sleep 1s
    lar -c ../reco1_keep.fcl -s prodsingle_sbnd_SinglesGen*_G4*_DetSim*.root
    sleep 1s
    lar -c ../run_pdsana.fcl -s prodsingle_sbnd_SinglesGen*_G4*_DetSim*.root
    sleep 1s
    mv larcv.root larcv_pdg$pdg\_P$p\_X$x\_Y$y\_Z$z\_thetaxz$thetaxz\_thetayz$thetayz\_t$t.root
    sleep 1s
    mv opana_tree.root opana_pdg$pdg\_P$p\_X$x\_Y$y\_Z$z\_thetaxz$thetaxz\_thetayz$thetayz\_t$t.root

    #Clean up
    rm prodsingle_sbnd_SinglesGen*.root
    rm hist*.root
    mv opana*.root larcv_*.root data/ #move to data folder

    #Increment counter
    run=$((run+1))
done



