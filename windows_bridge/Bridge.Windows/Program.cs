using SimControlStudio;
using SimControlStudio.Windows;

ApplicationConfiguration.Initialize();
Application.ThreadException += (_, e) => MessageBox.Show(e.Exception.Message, "SIM CONTROL STUDIO – hiba", MessageBoxButtons.OK, MessageBoxIcon.Error);
try { Application.Run(new MainForm()); }
catch (Exception error) { MessageBox.Show("A Bridge nem indítható. A helyi adatfájlok megmaradtak.\n" + error.Message, "SIM CONTROL STUDIO", MessageBoxButtons.OK, MessageBoxIcon.Error); }
