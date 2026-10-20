"""Installation automatique adaptee a la machine : detecte le GPU et installe le bon
onnxruntime (un seul des trois paquets, ils sont mutuellement exclusifs).

    python install.py            # installe
    python install.py --dry-run  # affiche seulement ce qui serait fait
"""
import platform
import shutil
import subprocess
import sys


def has_nvidia() -> bool:
    if shutil.which("nvidia-smi"):
        try:
            return subprocess.run(["nvidia-smi", "-L"], capture_output=True,
                                  timeout=10).returncode == 0
        except Exception:
            pass
    return False


def pick_onnxruntime() -> str:
    if has_nvidia():
        return "onnxruntime-gpu"
    if platform.system() == "Windows":
        return "onnxruntime-directml"  # AMD / Intel / tout GPU DirectX 12
    return "onnxruntime"


def pip(*pkgs: str, dry: bool, check: bool = True) -> bool:
    cmd = [sys.executable, "-m", "pip", "install", *pkgs]
    print(" ".join(cmd))
    if dry:
        return True
    return subprocess.run(cmd).returncode == 0 or not check


def main() -> None:
    dry = "--dry-run" in sys.argv
    ort_pkg = pick_onnxruntime()
    print(f"Paquet d'inference choisi : {ort_pkg}")
    pip("numpy", "opencv-python", "mss", "PySide6", dry=dry)
    if platform.system() == "Windows":
        # optionnels : s'ils echouent, le repli automatique utilisera mss
        pip("windows-capture", dry=dry, check=False)
        pip("dxcam", dry=dry, check=False)
    # evite le conflit entre variantes d'onnxruntime
    if not dry:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "onnxruntime",
                        "onnxruntime-gpu", "onnxruntime-directml"], capture_output=True)
    pip(ort_pkg, dry=dry)
    print("\nOptionnel (pour utiliser directement un .pt) : pip install ultralytics")


if __name__ == "__main__":
    main()
