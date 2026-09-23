for d in 0000:00:1c.4 0000:02:00.0 0000:03:00.0 0000:03:01.0 0000:03:02.0 0000:3a:00.0; do
    echo on | sudo tee /sys/bus/pci/devices/$d/power/control
done
