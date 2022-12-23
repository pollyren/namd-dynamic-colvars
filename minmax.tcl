# measures the boundaries of the protein
# Polly Ren, December 2022

proc measure_minmax {current_npt} {
    set psf  ubq-denatured-solvate-ionised.psf
    set dcd  ubq-consec-npt$current_npt.dcd
    mol load psf $psf dcd $dcd

    set sel [atomselect top "protein" frame last]
    set measure [measure minmax $sel]

    set outfile [open ./minmax_npt$current_npt.dat w]
    puts $outfile {$measure}
    $sel delete

    close $outfile
    mol delete top
}