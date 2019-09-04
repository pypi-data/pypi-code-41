def setup():
  import sys
  is_colab = 'google.colab' in sys.modules
  if is_colab:
    # Mounting Google Drive and add it to Python sys path

    google_drive_mount_point = '/content/google_drive'

    import os, sys, time
    from google.colab import drive
    drive.mount(google_drive_mount_point)

    google_drive = google_drive_mount_point + '/My Drive'
    google_drive_prefix = google_drive + '/prefix'

    if not os.path.isdir(google_drive_prefix): os.mkdir(google_drive_prefix)

    pyrosetta_install_prefix_path = '/content/prefix'
    if os.path.islink(pyrosetta_install_prefix_path): os.unlink(pyrosetta_install_prefix_path)
    os.symlink(google_drive_prefix, pyrosetta_install_prefix_path)

    for e in os.listdir(pyrosetta_install_prefix_path): sys.path.append(pyrosetta_install_prefix_path + '/' + e)
    return 1
  else:
    return 0
