from robusta.api import *



@action
def volume_analysis(event: PersistentVolumeEvent):
    # This function creates a reader pod (using the builtin hikaru library) that mount and output contents present on your persistent volume.
    """
    This action shows you the files present on your persistent volume
    """
    function_name = "volume_analysis"
    # https://docs.robusta.dev/master/developer-guide/actions/findings-api.html
    finding = Finding(
        title=f"Persistent Volume content",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )

    # Get persistent volume data the object contains data related to PV like metadata etc
    volume = event.get_persistentvolume()

    volume_claimref = volume.spec.claimRef
    if volume_claimref != None:
        try:
            pvc = PersistentVolumeClaim.readNamespacedPersistentVolumeClaim(
                name=volume_claimref.name, namespace=volume_claimref.namespace).obj
            print(pvc)
            print("hello")
            # config.load_kube_config()
            # v1 = client.CoreV1Api()
            # t1 = v1.read_namespaced_persistent_volume_claim_status(
            #     name=volume_claimref.name, namespace=volume_claimref.namespace)
            # print("hello1")
            # print(t1)

        except RuntimeError as e:
            finding.add_enrichment(
                [
                    MarkdownBlock(
                        f"*Args*\n```\n{e.args}\n```"
                    ),
                ]
            )
        except Exception as e:
            finding.add_enrichment(
                [
                    MarkdownBlock(
                        f"*Args*\n```\n{e.args}\n```"
                    ),
                ]
            )

    else:
        print("not hello")

    # # Define a reader (busybox) pod which mounts the volume

    # reader_pod_spec = RobustaPod(
    #     apiVersion="v1",
    #     kind="Pod",
    #     metadata=ObjectMeta(
    #         name="volume-inspector",
    #         namespace=volume.spec.claimRef.namespace,
    #     ),
    #     spec=PodSpec(
    #         volumes=[
    #             Volume(
    #                 name="pvc-mount",
    #                 persistentVolumeClaim=PersistentVolumeClaimVolumeSource(
    #                     claimName=volume.spec.claimRef.name
    #                 )
    #             )
    #         ],
    #         containers=[
    #             Container(
    #                 name="pvc-inspector",
    #                 image="busybox",
    #                 command=["tail"],
    #                 args=["-f", "/dev/null"],
    #                 volumeMounts=[
    #                     VolumeMount(
    #                         mountPath="/pvc",
    #                         name="pvc-mount",
    #                     )
    #                 ],
    #             )
    #         ]
    #     )
    # )
    # # create the pod defined
    # reader_pod = reader_pod_spec.create()

    # try:
    #     # https://docs.robusta.dev/master/developer-guide/actions/findings-api.html
    #     finding = Finding(
    #         title=f"Persistent Volume content",
    #         source=FindingSource.MANUAL,
    #         aggregation_key=function_name,
    #         finding_type=FindingType.REPORT,
    #         failure=False,
    #     )
    #     # exec a cmd on the reader pod to get file contents of PV
    #     cmd = f"ls -R /pvc"
    #     block_list: List[BaseBlock] = []
    #     output = reader_pod.exec(cmd)
    #     block_list.append(MarkdownBlock(
    #         f"Files currently present on your volume {volume.metadata.name} are:*"))
    #     block_list.append(FileBlock(output))
    #     finding.add_enrichment(block_list)
    #     event.add_finding(finding)
    # except:
    #     pass
    # finally:
    #     # delete the reader pod
    #     reader_pod.delete()
