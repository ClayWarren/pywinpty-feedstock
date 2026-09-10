# ARM64 counterpart of upstream src/configurations.gypi.
# Keep upstream winpty.gyp as the owner of sources, defines and libraries.
{
    'target_defaults': {
        'default_configuration': 'Release_ARM64',
        'configurations': {
            'Release_ARM64': {
                'msvs_configuration_platform': 'ARM64',
            },
        },
        'msvs_configuration_attributes': {
            'OutputDirectory': '$(SolutionDir)$(ConfigurationName)\\$(Platform)',
            'IntermediateDirectory': '$(ConfigurationName)\\$(Platform)\\obj\\$(ProjectName)',
        },
        'msvs_settings': {
            'VCLinkerTool': {
                'SubSystem': '1',
            },
            'VCCLCompilerTool': {
                'RuntimeLibrary': '2',  # /MD, matching conda-forge's CRT.
            },
        },
        'msbuild_toolset': 'v143',
    },
}
