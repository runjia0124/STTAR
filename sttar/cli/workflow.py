
def build_workflow(config_file, retval):
    """Create the Nipype Workflow that supports the whole execution graph."""
    from niworkflows.utils.bids import collect_participants, check_pipeline_version
    from niworkflows.reports import generate_reports
    from sttar import config
    from sttar.utils.misc import check_deps
    from sttar.workflows.base import init_sttar_wf

    config.load(config_file)
    build_log = config.loggers.workflow

    output_dir = config.execution.output_dir
    version = config.environment.version

    retval["return_code"] = 1
    retval["workflow"] = None

    # warn if older results exist: check for dataset_description.json in output folder
    msg = check_pipeline_version(
        version, output_dir / "dmriprep" / "dataset_description.json"
    )
    if msg is not None:
        build_log.warning(msg)

    # Please note this is the input folder's dataset_description.json
    dset_desc_path = config.execution.bids_dir / "dataset_description.json"
    if dset_desc_path.exists():
        from hashlib import sha256

        desc_content = dset_desc_path.read_bytes()
        config.execution.bids_description_hash = sha256(desc_content).hexdigest()

    # First check that bids_dir looks like a BIDS folder
    print('layout: ', config.execution.layout)
    print('label: ', config.execution.participant_label)
    subject_list = collect_participants(
        config.execution.layout, participant_label=config.execution.participant_label
    )

    # Called with reports only
    if config.execution.reports_only:
        from pkg_resources import resource_filename as pkgrf

        build_log.log(
            25, "Running --reports-only on participants %s", ", ".join(subject_list)
        )
        retval["return_code"] = generate_reports(
            subject_list,
            config.execution.output_dir,
            config.execution.run_uuid,
            config=pkgrf("dmriprep", "config/reports-spec.yml"),
            packagename="dmriprep",
        )
        return retval

    # Build main workflow
    INIT_MSG = """
    Running dMRIPrep version {version}:
      * BIDS dataset path: {bids_dir}.
      * Participant list: {subject_list}.
      * Run identifier: {uuid}.
      * Output spaces: {spaces}.
    """.format
    build_log.log(
        25,
        INIT_MSG(
            version=config.environment.version,
            bids_dir=config.execution.bids_dir,
            subject_list=subject_list,
            uuid=config.execution.run_uuid,
            spaces=config.execution.output_spaces,
        ),
    )

    retval["workflow"] = init_dmriprep_wf()

    # Check workflow for missing commands
    missing = check_deps(retval["workflow"])
    if missing:
        build_log.critical(
            "Cannot run dMRIPrep. Missing dependencies:%s",
            "\n\t* %s".join(
                ["{} (Interface: {})".format(cmd, iface) for iface, cmd in missing]
            ),
        )
        retval["return_code"] = 127  # 127 == command not found.
        return retval

    config.to_filename(config_file)
    build_log.info(
        "dMRIPrep workflow graph with %d nodes built successfully.",
        len(retval["workflow"]._get_all_nodes()),
    )
    retval["return_code"] = 0
    return retval

