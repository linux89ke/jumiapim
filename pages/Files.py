Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 542, in _run_script

    exec(code, module.__dict__)

  File "/mount/src/jumiapim/pages/Files.py", line 50, in <module>

    main()

  File "/mount/src/jumiapim/pages/Files.py", line 37, in main

    merged_df = merge_csv_files(uploaded_files)

                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/jumiapim/pages/Files.py", line 20, in merge_csv_files

    merged_df = pd.concat(dfs, axis=1, join='inner')

                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.11/site-packages/pandas/core/reshape/concat.py", line 395, in concat

    return op.get_result()

           ^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.11/site-packages/pandas/core/reshape/concat.py", line 680, in get_result

    indexers[ax] = obj_labels.get_indexer(new_labels)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/home/adminuser/venv/lib/python3.11/site-packages/pandas/core/indexes/base.py", line 3885, in get_indexer

    raise InvalidIndexError(self._requires_unique_msg)

pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects
