using System;
using LibreHardwareMonitor.Hardware;

namespace HardwareMonitor
{
    class Program
    {
        static void Main(string[] args)
        {
            Computer computer = new Computer
            {
                IsCpuEnabled = true
            };
            computer.Open();

            foreach (IHardware hardware in computer.Hardware)
            {
                if (hardware.HardwareType == HardwareType.Cpu)
                {
                    Console.WriteLine($"Hardware: {hardware.Name}");
                    hardware.Update();

                    foreach (ISensor sensor in hardware.Sensors)
                    {
                        if (sensor.SensorType == SensorType.Temperature)
                        {
                            Console.WriteLine($"Temperature Sensor: {sensor.Name} - Value: {sensor.Value.GetValueOrDefault()} °C");
                        }

                        if (sensor.SensorType == SensorType.Clock)
                        {
                            Console.WriteLine($"Clock Sensor: {sensor.Name} - Value: {sensor.Value.GetValueOrDefault()} MHz");
                        }
                    }
                }
            }

            computer.Close();
        }
    }
}
